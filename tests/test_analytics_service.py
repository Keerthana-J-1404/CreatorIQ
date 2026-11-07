import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from backend.main import app
from backend.routes.analytics import get_channel_analytics
from backend.routes.youtube import get_youtube_channel
from backend.schemas.youtube import ChannelInfo, ChannelRequest, ChannelResponse, VideoInfo
from backend.services.analytics_service import calculate_channel_analytics


def make_video(
    video_id: str,
    views: int | None,
    likes: int | None,
    comments: int | None,
) -> VideoInfo:
    return VideoInfo(
        video_id=video_id,
        title=f"Video {video_id}",
        description="",
        view_count=views,
        like_count=likes,
        comment_count=comments,
        url=f"https://www.youtube.com/watch?v={video_id}",
    )


def make_channel(videos: list[VideoInfo]) -> ChannelResponse:
    return ChannelResponse(
        channel=ChannelInfo(
            channel_id="channel-1",
            name="Creator",
            description="",
            total_views=1_000_000,
        ),
        videos=videos,
    )


class CalculateChannelAnalyticsTests(unittest.TestCase):
    def test_calculates_averages_rates_rankings_and_relative_performance(self) -> None:
        result = calculate_channel_analytics(
            make_channel(
                [
                    make_video("low", 100, 10, 5),
                    make_video("middle", 200, 20, 10),
                    make_video("high", 300, 30, 15),
                ]
            )
        )

        self.assertEqual(result.analytics.average_views_per_video, 200)
        self.assertEqual(result.analytics.average_likes_per_video, 20)
        self.assertEqual(result.analytics.average_comments_per_video, 10)
        self.assertAlmostEqual(result.analytics.average_engagement_rate_percent, 15)
        self.assertEqual(result.analytics.total_recent_video_views, 600)
        self.assertEqual(result.analytics.highest_viewed_video.video_id, "high")
        self.assertEqual(result.analytics.lowest_viewed_video.video_id, "low")
        self.assertEqual(result.videos[0].engagement_rate_percent, 15)
        self.assertEqual(result.videos[0].views_vs_average_percent, -50)
        self.assertEqual(result.videos[0].performance, "below_average")
        self.assertEqual(result.videos[2].performance, "above_average")

    def test_missing_likes_and_comments_are_excluded_not_zeroed(self) -> None:
        result = calculate_channel_analytics(
            make_channel(
                [
                    make_video("complete", 100, 10, 5),
                    make_video("missing", 300, None, None),
                ]
            )
        )

        self.assertEqual(result.analytics.average_views_per_video, 200)
        self.assertEqual(result.analytics.average_likes_per_video, 10)
        self.assertEqual(result.analytics.average_comments_per_video, 5)
        self.assertEqual(result.analytics.videos_with_like_data, 1)
        self.assertEqual(result.analytics.videos_with_comment_data, 1)
        self.assertIsNone(result.videos[1].engagement_rate_percent)
        self.assertEqual(result.analytics.average_engagement_rate_percent, 15)

    def test_zero_views_have_no_engagement_rate_or_division_error(self) -> None:
        result = calculate_channel_analytics(
            make_channel([make_video("zero", 0, 5, 2)])
        )

        self.assertEqual(result.analytics.total_recent_video_views, 0)
        self.assertIsNone(result.videos[0].engagement_rate_percent)
        self.assertIsNone(result.videos[0].views_vs_average_percent)
        self.assertEqual(result.videos[0].performance, "at_average")
        self.assertIsNone(result.analytics.average_engagement_rate_percent)

    def test_empty_video_list_has_no_averages_totals_or_rankings(self) -> None:
        result = calculate_channel_analytics(make_channel([]))

        self.assertEqual(result.videos, [])
        self.assertEqual(result.analytics.recent_video_count, 0)
        self.assertIsNone(result.analytics.average_views_per_video)
        self.assertIsNone(result.analytics.average_likes_per_video)
        self.assertIsNone(result.analytics.average_comments_per_video)
        self.assertIsNone(result.analytics.average_engagement_rate_percent)
        self.assertIsNone(result.analytics.total_recent_video_views)
        self.assertIsNone(result.analytics.highest_viewed_video)
        self.assertIsNone(result.analytics.lowest_viewed_video)

    def test_missing_view_data_is_not_counted_as_zero(self) -> None:
        result = calculate_channel_analytics(
            make_channel(
                [
                    make_video("known", 100, None, None),
                    make_video("unknown", None, None, None),
                ]
            )
        )

        self.assertEqual(result.analytics.total_recent_video_views, 100)
        self.assertEqual(result.analytics.average_views_per_video, 100)
        self.assertEqual(result.analytics.videos_with_view_data, 1)
        self.assertIsNone(result.videos[1].views_vs_average_percent)
        self.assertEqual(result.videos[1].performance, "unavailable")

    def test_original_youtube_endpoint_contract_remains_unchanged(self) -> None:
        channel_data = make_channel([make_video("sample", 10, 1, 0)])
        with patch(
            "backend.routes.youtube.get_channel_data",
            new=AsyncMock(return_value=channel_data),
        ) as get_channel_data:
            result = asyncio.run(
                get_youtube_channel(ChannelRequest(channel_url="https://youtube.com/@creator"))
            )

        get_channel_data.assert_awaited_once_with("https://youtube.com/@creator")
        self.assertEqual(result, channel_data)
        self.assertEqual(set(result.model_dump()), {"channel", "videos"})
        openapi = app.openapi()
        original_endpoint = openapi["paths"]["/api/youtube/channel"]["post"]
        response_schema = original_endpoint["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        self.assertEqual(response_schema["$ref"], "#/components/schemas/ChannelResponse")
        self.assertIsInstance(result, ChannelResponse)

    def test_analytics_endpoint_reuses_youtube_service(self) -> None:
        channel_data = make_channel([make_video("sample", 100, 10, 5)])
        with patch(
            "backend.routes.analytics.get_channel_data",
            new=AsyncMock(return_value=channel_data),
        ) as get_channel_data:
            result = asyncio.run(
                get_channel_analytics(
                    ChannelRequest(channel_url="https://youtube.com/@creator")
                )
            )

        get_channel_data.assert_awaited_once_with("https://youtube.com/@creator")
        self.assertEqual(result.analytics.total_recent_video_views, 100)
        openapi = app.openapi()
        analytics_endpoint = openapi["paths"]["/api/analytics/channel"]["post"]
        response_schema = analytics_endpoint["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        self.assertEqual(
            response_schema["$ref"], "#/components/schemas/AnalyticsChannelResponse"
        )


if __name__ == "__main__":
    unittest.main()
