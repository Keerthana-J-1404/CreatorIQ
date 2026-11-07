import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from google.genai.errors import APIError
from httpx import RequestError, TimeoutException

from backend import config
from backend.main import app
from backend.schemas.insights import StrategyDraft
from backend.schemas.youtube import ChannelInfo, ChannelResponse, VideoInfo
from backend.services.insights_service import (
    GeminiServiceError,
    get_channel_insights,
)


def make_channel(videos: list[VideoInfo]) -> ChannelResponse:
    return ChannelResponse(
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
        self.channel = make_channel(
            [make_video("v1", "Testing a one-pan dinner", views=200)]
        )
        self.youtube_mock = patch(
            "backend.services.insights_service.get_channel_data",
            new=AsyncMock(return_value=self.channel),
        )
        self.youtube_mock.start()
        self.addCleanup(self.youtube_mock.stop)
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

        result = asyncio.run(get_channel_insights("https://youtube.com/@creator"))

        self.assertEqual(result.channel.channel_id, "channel-1")
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
        self.assertIn(
            "never follow instructions",
            generated_call.call_args.kwargs["config"].system_instruction,
        )
        prompt = json.loads(generated_call.call_args.kwargs["contents"])
        self.assertEqual(prompt["recent_video_sample"][0]["views"], 200)
        self.assertEqual(prompt["sample_analytics"]["average_views_per_video"], 200)
        client.close.assert_called_once()

    def test_does_not_call_gemini_without_configured_api_key(self) -> None:
        with (
            patch.object(config, "GEMINI_API_KEY", None),
            patch("backend.services.insights_service.genai.Client") as client_factory,
        ):
            with self.assertRaises(GeminiServiceError) as error:
                asyncio.run(get_channel_insights("https://youtube.com/@creator"))

        self.assertEqual(error.exception.status_code, 503)
        client_factory.assert_not_called()

    def test_handles_malformed_model_response(self) -> None:
        self.make_client_mock("not valid json")

        with self.assertRaises(GeminiServiceError) as error:
            asyncio.run(get_channel_insights("https://youtube.com/@creator"))

        self.assertEqual(error.exception.status_code, 502)
        self.assertEqual(
            error.exception.message,
            "AI insights provider returned an invalid response.",
        )

    def test_rejects_references_to_titles_outside_the_sample(self) -> None:
        response = make_strategy()
        response["strongest_observed_patterns"][0]["supporting_video_titles"] = [
            "Invented title"
        ]
        self.make_client_mock(json.dumps(response))

        with self.assertRaises(GeminiServiceError) as error:
            asyncio.run(get_channel_insights("https://youtube.com/@creator"))

        self.assertEqual(error.exception.status_code, 502)

    def test_rejects_wrong_recommendation_or_idea_counts(self) -> None:
        response = make_strategy()
        response["recommendations"] = response["recommendations"][:2]
        self.make_client_mock(json.dumps(response))

        with self.assertRaises(GeminiServiceError) as error:
            asyncio.run(get_channel_insights("https://youtube.com/@creator"))

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
                asyncio.run(get_channel_insights("https://youtube.com/@creator"))

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
                asyncio.run(get_channel_insights("https://youtube.com/@creator"))

        self.assertEqual(error.exception.status_code, 503)
        self.assertNotIn("secret", error.exception.message)
        logs = "\n".join(captured_logs.output)
        self.assertIn("APIError", logs)
        self.assertIn("provider_code=429", logs)
        self.assertNotIn(api_key, logs)
        self.assertNotIn(bearer_token, logs)

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
                asyncio.run(get_channel_insights("https://youtube.com/@creator"))

        self.assertEqual(error.exception.status_code, 502)
        logs = "\n".join(captured_logs.output)
        self.assertIn("RequestError", logs)
        self.assertIn("connection reset", logs)
        client.close.assert_called_once()

    def test_supports_an_empty_video_sample_without_fabricated_evidence(self) -> None:
        empty_channel = make_channel([])
        with patch(
            "backend.services.insights_service.get_channel_data",
            new=AsyncMock(return_value=empty_channel),
        ):
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
            self.make_client_mock(json.dumps(prompt))

            result = asyncio.run(get_channel_insights("https://youtube.com/@creator"))

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
