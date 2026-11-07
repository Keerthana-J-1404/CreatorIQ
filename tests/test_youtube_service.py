import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from backend.services import youtube_service
from backend.services.youtube_service import YouTubeServiceError, get_channel_data


CHANNEL_URL = "https://www.youtube.com/@creator"


def channel_payload() -> dict[str, object]:
    return {
        "items": [
            {
                "id": "real-channel-id",
                "snippet": {
                    "title": "Real Creator",
                    "description": "A real YouTube channel.",
                    "thumbnails": {},
                },
                "statistics": {
                    "subscriberCount": "1234",
                    "viewCount": "56789",
                    "videoCount": "42",
                },
                "contentDetails": {"relatedPlaylists": {"uploads": "uploads-id"}},
            }
        ]
    }


class YouTubeServiceDataSourceTests(unittest.TestCase):
    def test_missing_or_placeholder_key_returns_explicit_demo_data(self) -> None:
        api_keys = (
            None,
            "",
            "  ",
            "your_youtube_api_key_here",
            " YOUR_YOUTUBE_API_KEY_HERE ",
        )
        for api_key in api_keys:
            with self.subTest(api_key=api_key):
                with (
                    patch.object(youtube_service, "YOUTUBE_API_KEY", api_key),
                    patch(
                        "backend.services.youtube_service._api_get",
                        new=AsyncMock(),
                    ) as api_get,
                ):
                    result = asyncio.run(get_channel_data(CHANNEL_URL))

                self.assertEqual(result.data_source, "demo")
                self.assertEqual(result.channel.channel_id, "mock_channel_id_12345")
                self.assertTrue(result.videos)
                api_get.assert_not_awaited()

    def test_configured_key_returns_explicit_youtube_data(self) -> None:
        with (
            patch.object(youtube_service, "YOUTUBE_API_KEY", "configured-key"),
            patch(
                "backend.services.youtube_service._api_get",
                new=AsyncMock(
                    side_effect=[
                        channel_payload(),
                        {
                            "items": [
                                {
                                    "snippet": {
                                        "resourceId": {"videoId": "real-video-id"}
                                    }
                                }
                            ]
                        },
                        {
                            "items": [
                                {
                                    "id": "real-video-id",
                                    "snippet": {
                                        "title": "Real video",
                                        "description": "Real description",
                                        "publishedAt": "2026-01-01T00:00:00Z",
                                        "thumbnails": {},
                                    },
                                    "statistics": {
                                        "viewCount": "100",
                                        "likeCount": "10",
                                        "commentCount": "2",
                                    },
                                }
                            ]
                        },
                    ]
                ),
            ) as api_get,
        ):
            result = asyncio.run(get_channel_data(CHANNEL_URL))

        self.assertEqual(result.data_source, "youtube_api")
        self.assertEqual(result.channel.channel_id, "real-channel-id")
        self.assertEqual(result.channel.subscriber_count, 1234)
        self.assertEqual(result.videos[0].video_id, "real-video-id")
        self.assertEqual(result.videos[0].view_count, 100)
        self.assertEqual(api_get.await_count, 3)

    def test_configured_api_failure_is_not_replaced_with_demo_data(self) -> None:
        api_error = YouTubeServiceError("YouTube API quota or rate limit exceeded.", 429)
        with (
            patch.object(youtube_service, "YOUTUBE_API_KEY", "configured-key"),
            patch(
                "backend.services.youtube_service._api_get",
                new=AsyncMock(side_effect=api_error),
            ) as api_get,
        ):
            with self.assertRaises(YouTubeServiceError) as raised:
                asyncio.run(get_channel_data(CHANNEL_URL))

        self.assertIs(raised.exception, api_error)
        api_get.assert_awaited_once()

    def test_video_fetch_failure_is_not_replaced_with_demo_data(self) -> None:
        api_error = YouTubeServiceError("YouTube API is temporarily unavailable.", 502)
        with (
            patch.object(youtube_service, "YOUTUBE_API_KEY", "configured-key"),
            patch(
                "backend.services.youtube_service._api_get",
                new=AsyncMock(
                    side_effect=[
                        channel_payload(),
                        api_error,
                    ]
                ),
            ) as api_get,
        ):
            with self.assertRaises(YouTubeServiceError) as raised:
                asyncio.run(get_channel_data(CHANNEL_URL))

        self.assertIs(raised.exception, api_error)
        self.assertEqual(api_get.await_count, 2)


if __name__ == "__main__":
    unittest.main()
