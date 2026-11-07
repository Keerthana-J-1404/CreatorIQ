import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from google.genai.errors import APIError
from httpx import RequestError, TimeoutException

from backend import config
from backend.main import app
from backend.schemas.analytics import AnalyticsChannelResponse
from backend.routes.analytics import get_channel_analytics
from backend.schemas.insights import StrategyDraft
from backend.schemas.youtube import (
    ChannelInfo,
    ChannelRequest,
    ChannelResponse,
    VideoInfo,
)
from backend.routes.insights import get_channel_content_strategy
from backend.services.analytics_service import calculate_channel_analytics
from backend.services.analytics_snapshot_service import _clear_analytics_snapshot_cache
from backend.services.insights_service import (
    GeminiServiceError,
    _build_prompt_data,
    _validate_draft_references,
    get_channel_insights,
)
from backend.services.youtube_service import YouTubeServiceError


def make_channel(videos: list[VideoInfo]) -> ChannelResponse:
    return ChannelResponse(
        data_source="youtube_api",
        channel=ChannelInfo(
            channel_id="channel-1",
            name="Creator",
            description="Cooking and kitchen experiments",
            total_views=1_000_000,
        ),
        videos=videos,
    )


def make_video(
    video_id: str,
    title: str,
    views: int | None = 100,
    likes: int | None = 10,
    comments: int | None = 5,
    description: str = "A kitchen experiment.",
) -> VideoInfo:
    return VideoInfo(
        video_id=video_id,
        title=title,
        description=description,
        view_count=views,
        like_count=likes,
        comment_count=comments,
        url=f"https://www.youtube.com/watch?v={video_id}",
    )


def make_strategy(title: str = "Testing a one-pan dinner") -> dict[str, object]:
    return {
        "assessment": "The sample contains one video with recorded metrics.",
        "strongest_observed_patterns": [
            {
                "observation": "The available video has measurable engagement.",
                "supporting_video_titles": [title],
            }
        ],
        "weakest_observed_patterns": [],
        "content_patterns": [
            {
                "category": "format",
                "description": "A kitchen experiment format appears in the sample.",
                "supporting_video_titles": [title],
                "performance_observation": None,
            }
        ],
        "content_gaps": {
            "observed_underrepresented": [],
            "hypotheses_to_test": [
                {
                    "hypothesis": "A comparison format may be worth testing.",
                    "rationale": "This is a testable idea based on the sample topic.",
                    "supporting_video_titles": [title],
                }
            ],
        },
        "recommendations": [
            {
                "recommendation": f"Test a follow-up to {title}.",
                "rationale": "It directly builds on the observed sample topic.",
                "supporting_video_titles": [title],
            },
            {
                "recommendation": "Compare another format.",
                "rationale": "A controlled test could add evidence.",
                "supporting_video_titles": [],
            },
            {
                "recommendation": "Review performance after more uploads.",
                "rationale": "The sample is limited.",
                "supporting_video_titles": [],
            },
        ],
        "content_ideas": [
            {
                "proposed_title": f"New idea {index}",
                "explanation": "A tentative idea based on the channel context.",
                "based_on_video_titles": [title],
            }
            for index in range(1, 6)
        ],
    }


class ChannelInsightsServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_analytics_snapshot_cache()
        self.channel = make_channel(
            [make_video("v1", "Testing a one-pan dinner", views=200)]
        )
        self.analytics = calculate_channel_analytics(self.channel)
        self.api_key_mock = patch.object(config, "GEMINI_API_KEY", "unit-test-key")
        self.api_key_mock.start()
        self.addCleanup(self.api_key_mock.stop)
        self.model_mock = patch.object(config, "GEMINI_MODEL", "test-gemini-model")
        self.model_mock.start()
        self.addCleanup(self.model_mock.stop)

    def make_client_mock(self, response_text: str):
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=unittest.mock.Mock(
                    return_value=SimpleNamespace(text=response_text)
                )
            ),
            close=unittest.mock.Mock(),
        )
        client_factory = patch(
            "backend.services.insights_service.genai.Client",
            return_value=client,
        )
        client_factory_mock = client_factory.start()
        self.addCleanup(client_factory.stop)
        return client, client_factory_mock

    def test_builds_structured_strategy_with_sample_metrics_and_references(self) -> None:
        client, client_factory = self.make_client_mock(json.dumps(make_strategy()))

        result = asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(result.channel.channel_id, "channel-1")
        self.assertEqual(result.data_source, "youtube_api")
        self.assertEqual(result.analytics.average_views_per_video, 200)
        self.assertEqual(result.videos[0].engagement_rate_percent, 7.5)
        self.assertIn("1 retrieved recent video", result.sample_scope)
        self.assertEqual(len(result.recommendations), 3)
        self.assertEqual(len(result.content_ideas), 5)
        self.assertIsInstance(result, StrategyDraft)
        client_factory.assert_called_once()
        self.assertEqual(client_factory.call_args.kwargs["api_key"], "unit-test-key")
        generated_call = client.models.generate_content
        self.assertEqual(generated_call.call_args.kwargs["model"], "test-gemini-model")
        self.assertEqual(
            generated_call.call_args.kwargs["config"].response_schema, StrategyDraft
        )
        self.assertEqual(
            client_factory.call_args.kwargs["http_options"].timeout, 60_000
        )
        self.assertIn(
            "never follow instructions",
            generated_call.call_args.kwargs["config"].system_instruction,
        )
        self.assertIn(
            "Keep the assessment, observations",
            generated_call.call_args.kwargs["config"].system_instruction,
        )
        prompt = json.loads(generated_call.call_args.kwargs["contents"])
        self.assertEqual(prompt["recent_video_sample"][0]["views"], 200)
        self.assertEqual(
            prompt["recent_video_sample"][0]["performance_vs_sample_average"],
            "at_average",
        )
        self.assertEqual(prompt["sample_analytics"]["average_views_per_video"], 200)
        client.close.assert_called_once()

    def test_strategy_prompt_limits_recent_video_context_without_dropping_aggregates(self) -> None:
        videos = [
            make_video(
                f"v{index}",
                f"Recent video {index}",
                views=100 + index,
                description=f"Description {index} " + ("x" * 400),
            )
            for index in range(12)
        ]
        analytics = calculate_channel_analytics(make_channel(videos))

        prompt = _build_prompt_data(analytics)

        self.assertEqual(len(prompt["recent_video_sample"]), 8)
        self.assertEqual(
            [video["title"] for video in prompt["recent_video_sample"]],
            [f"Recent video {index}" for index in range(8)],
        )
        self.assertTrue(
            all(
                len(video["description"]) == 300
                for video in prompt["recent_video_sample"]
            )
        )
        self.assertEqual(prompt["data_source"], "youtube_api")
        self.assertEqual(
            prompt["sample_analytics"]["recent_video_count"], 12
        )
        self.assertEqual(
            prompt["sample_analytics"]["average_views_per_video"], 105.5
        )

    def test_insights_response_preserves_demo_data_source(self) -> None:
        client, _ = self.make_client_mock(json.dumps(make_strategy()))
        demo_analytics = self.analytics.model_copy(update={"data_source": "demo"})
        result = asyncio.run(get_channel_insights(demo_analytics))

        self.assertEqual(result.data_source, "demo")
        self.assertIn("Demo data; illustrative only", result.sample_scope)
        client.close.assert_called_once()

    def test_rejects_missing_or_invalid_analytics(self) -> None:
        for invalid_analytics in (None, {}, {"data_source": "invalid"}):
            with self.subTest(analytics=invalid_analytics):
                with self.assertRaises(GeminiServiceError) as error:
                    asyncio.run(get_channel_insights(invalid_analytics))

                self.assertEqual(error.exception.status_code, 422)
                self.assertEqual(
                    error.exception.message, "Analytics data is missing or invalid."
                )

    def test_revalidates_invalid_analytics_model_instances(self) -> None:
        invalid_source = AnalyticsChannelResponse.model_construct(
            data_source="invalid",
            channel=self.analytics.channel,
            videos=self.analytics.videos,
            analytics=self.analytics.analytics,
        )
        malformed_nested_analytics = AnalyticsChannelResponse.model_construct(
            data_source="youtube_api",
            channel=self.analytics.channel,
            videos=self.analytics.videos,
            analytics={"recent_video_count": "not-an-integer"},
        )

        for invalid_analytics in (invalid_source, malformed_nested_analytics):
            with self.subTest(analytics=invalid_analytics):
                with self.assertRaises(GeminiServiceError) as error:
                    asyncio.run(get_channel_insights(invalid_analytics))

                self.assertEqual(error.exception.status_code, 422)
                self.assertEqual(
                    error.exception.message, "Analytics data is missing or invalid."
                )

    def test_insights_endpoint_passes_shared_snapshot_to_gemini_service(self) -> None:
        expected = object()
        with (
            patch(
                "backend.routes.insights.get_analytics_snapshot",
                new_callable=AsyncMock,
                return_value=self.analytics,
            ) as get_snapshot,
            patch(
                "backend.routes.insights.get_channel_insights",
                new_callable=AsyncMock,
                return_value=expected,
            ) as get_insights,
        ):
            result = asyncio.run(
                get_channel_content_strategy(
                    ChannelRequest(channel_url="https://youtube.com/@creator")
                )
            )

        self.assertIs(result, expected)
        get_snapshot.assert_awaited_once_with("https://youtube.com/@creator")
        get_insights.assert_awaited_once_with(self.analytics)

    def test_insights_endpoint_maps_youtube_and_gemini_failures(self) -> None:
        request = ChannelRequest(channel_url="https://youtube.com/@creator")
        youtube_error = YouTubeServiceError("YouTube is unavailable.", 502)
        with patch(
            "backend.routes.insights.get_analytics_snapshot",
            new_callable=AsyncMock,
            side_effect=youtube_error,
        ):
            with self.assertRaises(HTTPException) as error:
                asyncio.run(get_channel_content_strategy(request))
        self.assertEqual(error.exception.status_code, 502)

        gemini_error = GeminiServiceError("Gemini is unavailable.", 503)
        with (
            patch(
                "backend.routes.insights.get_analytics_snapshot",
                new_callable=AsyncMock,
                return_value=self.analytics,
            ),
            patch(
                "backend.routes.insights.get_channel_insights",
                new_callable=AsyncMock,
                side_effect=gemini_error,
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                asyncio.run(get_channel_content_strategy(request))

        self.assertEqual(error.exception.status_code, 503)

    def test_analytics_and_insights_routes_share_one_snapshot(self) -> None:
        with (
            patch(
                "backend.services.analytics_snapshot_service.get_channel_data",
                new=AsyncMock(return_value=self.channel),
            ) as get_channel_data,
            patch(
                "backend.services.insights_service._generate_strategy",
                return_value=StrategyDraft.model_validate(make_strategy()),
            ),
        ):
            async def call_endpoints():
                request = ChannelRequest(channel_url="https://youtube.com/@creator")
                analytics = await get_channel_analytics(request)
                insights = await get_channel_content_strategy(request)
                return analytics, insights

            analytics, insights = asyncio.run(call_endpoints())

        get_channel_data.assert_awaited_once_with("https://youtube.com/@creator")
        self.assertEqual(analytics.data_source, "youtube_api")
        self.assertEqual(insights.data_source, "youtube_api")
        self.assertEqual(insights.analytics, analytics.analytics)

    def test_does_not_call_gemini_without_configured_api_key(self) -> None:
        with (
            patch.object(config, "GEMINI_API_KEY", None),
            patch("backend.services.insights_service.genai.Client") as client_factory,
        ):
            with self.assertRaises(GeminiServiceError) as error:
                asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 503)
        client_factory.assert_not_called()

    def test_handles_malformed_model_response(self) -> None:
        self.make_client_mock("not valid json")

        with self.assertRaises(GeminiServiceError) as error:
            asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 502)
        self.assertEqual(
            error.exception.message,
            "AI insights provider returned an invalid response.",
        )

    def test_discards_invalid_references_and_preserves_exact_valid_titles(self) -> None:
        response = make_strategy()
        valid_title = "Testing a one-pan dinner"
        invalid_title = "Invented title"
        api_key_like_title = "AIzaSyDUMMY0123456789abcdefghijklmnop"
        response["strongest_observed_patterns"][0][
            "supporting_video_titles"
        ] = [valid_title, invalid_title]
        response["weakest_observed_patterns"] = [
            {
                "observation": "A test observation.",
                "supporting_video_titles": [invalid_title, valid_title],
            }
        ]
        response["content_patterns"][0]["supporting_video_titles"] = [
            invalid_title,
            valid_title,
        ]
        response["content_gaps"]["observed_underrepresented"] = [
            {
                "observation": "A test content gap.",
                "supporting_video_titles": [valid_title, invalid_title],
            }
        ]
        response["content_gaps"]["hypotheses_to_test"][0][
            "supporting_video_titles"
        ] = [invalid_title, valid_title]
        response["recommendations"][0]["supporting_video_titles"] = [
            valid_title,
            invalid_title,
        ]
        response["recommendations"][1]["supporting_video_titles"] = [invalid_title]
        response["recommendations"][2]["supporting_video_titles"] = [
            api_key_like_title
        ]
        response["content_ideas"][0]["based_on_video_titles"] = [
            invalid_title,
            valid_title,
        ]
        response["content_ideas"][1]["based_on_video_titles"] = [invalid_title]
        draft = StrategyDraft.model_validate(response)

        with self.assertLogs(
            "backend.services.insights_service", level="WARNING"
        ) as captured_logs:
            _validate_draft_references(draft, self.analytics)

        self.assertEqual(
            draft.strongest_observed_patterns[0].supporting_video_titles,
            [valid_title],
        )
        self.assertEqual(
            draft.weakest_observed_patterns[0].supporting_video_titles,
            [valid_title],
        )
        self.assertEqual(
            draft.content_patterns[0].supporting_video_titles, [valid_title]
        )
        self.assertEqual(
            draft.content_gaps.observed_underrepresented[0].supporting_video_titles,
            [valid_title],
        )
        self.assertEqual(
            draft.content_gaps.hypotheses_to_test[0].supporting_video_titles,
            [valid_title],
        )
        self.assertEqual(
            draft.recommendations[0].supporting_video_titles, [valid_title]
        )
        self.assertEqual(draft.recommendations[1].supporting_video_titles, [])
        self.assertEqual(draft.recommendations[2].supporting_video_titles, [])
        self.assertEqual(draft.content_ideas[0].based_on_video_titles, [valid_title])
        self.assertEqual(draft.content_ideas[1].based_on_video_titles, [])
        self.assertIn(
            "discarded invalid supporting video references", captured_logs.output[0]
        )
        self.assertIn(invalid_title, captured_logs.output[0])
        self.assertNotIn(api_key_like_title, captured_logs.output[0])

    def test_discards_all_invalid_references_without_rejecting_strategy(self) -> None:
        response = make_strategy()
        for observation in response["strongest_observed_patterns"]:
            observation["supporting_video_titles"] = ["Not a retrieved title"]
        response["content_patterns"][0]["supporting_video_titles"] = [
            "Not a retrieved title"
        ]
        response["recommendations"][0]["supporting_video_titles"] = [
            "Not a retrieved title"
        ]
        response["content_ideas"][0]["based_on_video_titles"] = [
            "Not a retrieved title"
        ]
        draft = StrategyDraft.model_validate(response)

        _validate_draft_references(draft, self.analytics)

        self.assertEqual(
            draft.strongest_observed_patterns[0].supporting_video_titles, []
        )
        self.assertEqual(draft.content_patterns[0].supporting_video_titles, [])
        self.assertEqual(draft.recommendations[0].supporting_video_titles, [])
        self.assertEqual(draft.content_ideas[0].based_on_video_titles, [])

    def test_clears_references_when_no_video_titles_are_available(self) -> None:
        response = make_strategy()
        response["weakest_observed_patterns"] = [
            {
                "observation": "A test weak pattern.",
                "supporting_video_titles": ["Testing a one-pan dinner"],
            }
        ]
        response["content_gaps"]["observed_underrepresented"] = [
            {
                "observation": "A test gap.",
                "supporting_video_titles": ["Testing a one-pan dinner"],
            }
        ]
        draft = StrategyDraft.model_validate(response)
        empty_analytics = calculate_channel_analytics(make_channel([]))

        _validate_draft_references(draft, empty_analytics)

        reference_lists = [
            *(
                observation.supporting_video_titles
                for observation in (
                    *draft.strongest_observed_patterns,
                    *draft.weakest_observed_patterns,
                    *draft.content_gaps.observed_underrepresented,
                )
            ),
            *(
                hypothesis.supporting_video_titles
                for hypothesis in draft.content_gaps.hypotheses_to_test
            ),
            *(pattern.supporting_video_titles for pattern in draft.content_patterns),
            *(
                recommendation.supporting_video_titles
                for recommendation in draft.recommendations
            ),
            *(idea.based_on_video_titles for idea in draft.content_ideas),
        ]
        self.assertTrue(all(not titles for titles in reference_lists))

    def test_rejects_wrong_recommendation_or_idea_counts(self) -> None:
        response = make_strategy()
        response["recommendations"] = response["recommendations"][:2]
        self.make_client_mock(json.dumps(response))

        with self.assertRaises(GeminiServiceError) as error:
            asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 502)

    def test_maps_provider_timeout_to_gateway_timeout(self) -> None:
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=unittest.mock.Mock(
                    side_effect=TimeoutException("request timed out")
                )
            ),
            close=unittest.mock.Mock(),
        )
        client_factory = patch(
            "backend.services.insights_service.genai.Client",
            return_value=client,
        )
        client_factory.start()
        self.addCleanup(client_factory.stop)

        with self.assertLogs(
            "backend.services.insights_service", level="ERROR"
        ) as captured_logs:
            with self.assertRaises(GeminiServiceError) as error:
                asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 504)
        self.assertIn("TimeoutException", "\n".join(captured_logs.output))
        client.close.assert_called_once()

    def test_hides_provider_error_details(self) -> None:
        api_key = "AIzaSyDUMMY0123456789abcdefghijklmnop"
        bearer_token = "unit-test-bearer-token"
        provider_error = APIError(
            429,
            {
                "message": (
                    f"API key={api_key}; Authorization: Bearer {bearer_token}"
                )
            },
        )
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=unittest.mock.Mock(side_effect=provider_error)
            ),
            close=unittest.mock.Mock(),
        )
        client_factory = patch(
            "backend.services.insights_service.genai.Client",
            return_value=client,
        )
        client_factory.start()
        self.addCleanup(client_factory.stop)

        with self.assertLogs(
            "backend.services.insights_service", level="ERROR"
        ) as captured_logs:
            with self.assertRaises(GeminiServiceError) as error:
                asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 503)
        self.assertNotIn("secret", error.exception.message)
        logs = "\n".join(captured_logs.output)
        self.assertIn("APIError", logs)
        self.assertIn("provider_code=429", logs)
        self.assertNotIn(api_key, logs)
        self.assertNotIn(bearer_token, logs)

    def test_maps_gemini_deadline_exceeded_to_safe_gateway_timeout(self) -> None:
        provider_error = APIError(
            504,
            {"message": "DEADLINE_EXCEEDED internal provider details"},
        )
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=unittest.mock.Mock(side_effect=provider_error)
            ),
            close=unittest.mock.Mock(),
        )
        client_factory = patch(
            "backend.services.insights_service.genai.Client",
            return_value=client,
        )
        client_factory.start()
        self.addCleanup(client_factory.stop)

        with self.assertLogs(
            "backend.services.insights_service", level="ERROR"
        ) as captured_logs:
            with self.assertRaises(GeminiServiceError) as error:
                asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 504)
        self.assertEqual(error.exception.message, "AI insights request timed out.")
        self.assertNotIn("DEADLINE_EXCEEDED", error.exception.message)
        self.assertIn("provider_code=504", "\n".join(captured_logs.output))
        client.close.assert_called_once()

    def test_logs_request_error_type_and_safe_details(self) -> None:
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=unittest.mock.Mock(
                    side_effect=RequestError("connection reset")
                )
            ),
            close=unittest.mock.Mock(),
        )
        client_factory = patch(
            "backend.services.insights_service.genai.Client",
            return_value=client,
        )
        client_factory.start()
        self.addCleanup(client_factory.stop)

        with self.assertLogs(
            "backend.services.insights_service", level="ERROR"
        ) as captured_logs:
            with self.assertRaises(GeminiServiceError) as error:
                asyncio.run(get_channel_insights(self.analytics))

        self.assertEqual(error.exception.status_code, 502)
        logs = "\n".join(captured_logs.output)
        self.assertIn("RequestError", logs)
        self.assertIn("connection reset", logs)
        client.close.assert_called_once()

    def test_supports_an_empty_video_sample_without_fabricated_evidence(self) -> None:
        empty_channel = make_channel([])
        empty_analytics = calculate_channel_analytics(empty_channel)
        with patch(
            "backend.services.insights_service._generate_strategy"
        ) as generate_strategy:
            prompt = make_strategy()
            prompt["strongest_observed_patterns"] = []
            prompt["weakest_observed_patterns"] = []
            prompt["content_patterns"] = []
            prompt["content_gaps"]["hypotheses_to_test"] = [
                {
                    "hypothesis": (
                        "A topic suggested by the channel description may be tested."
                    ),
                    "rationale": "The channel description offers limited context.",
                    "supporting_video_titles": [],
                }
            ]
            prompt["recommendations"] = [
                {
                    "recommendation": f"Start by testing idea {index}.",
                    "rationale": "No recent video sample is available.",
                    "supporting_video_titles": [],
                }
                for index in range(1, 4)
            ]
            prompt["content_ideas"] = [
                {
                    "proposed_title": f"Exploratory idea {index}",
                    "explanation": "This is exploratory because no recent videos were retrieved.",
                    "based_on_video_titles": [],
                }
                for index in range(1, 6)
            ]
            generate_strategy.return_value = StrategyDraft.model_validate(prompt)

            result = asyncio.run(get_channel_insights(empty_analytics))

        self.assertEqual(result.videos, [])
        self.assertEqual(result.analytics.recent_video_count, 0)
        self.assertIn("No recent videos were retrieved", result.sample_scope)

    def test_registers_the_insights_endpoint_with_a_typed_response(self) -> None:
        endpoint = app.openapi()["paths"]["/api/insights/channel"]["post"]
        response_schema = endpoint["responses"]["200"]["content"][
            "application/json"
        ]["schema"]

        self.assertEqual(
            response_schema["$ref"], "#/components/schemas/ChannelInsightsResponse"
        )


if __name__ == "__main__":
    unittest.main()
