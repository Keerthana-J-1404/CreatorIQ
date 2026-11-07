import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from backend.main import app
from backend.routes.analytics import get_channel_analytics
from backend.routes.youtube import get_youtube_channel
from backend.schemas.youtube import ChannelInfo, ChannelRequest, ChannelResponse, VideoInfo
from backend.services.analytics_service import calculate_channel_analytics
from backend.services.analytics_snapshot_service import (
    MAX_ANALYTICS_SNAPSHOTS,
    _cache_key,
    _clear_analytics_snapshot_cache,
    get_analytics_snapshot,
)
from backend.services.youtube_service import YouTubeServiceError
from backend.services import analytics_snapshot_service


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
        data_source="youtube_api",
        channel=ChannelInfo(
            channel_id="channel-1",
            name="Creator",
            description="",
            total_views=1_000_000,
        ),
        videos=videos,
    )


class CalculateChannelAnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_analytics_snapshot_cache()

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

    def test_analytics_response_preserves_demo_data_source(self) -> None:
        channel_data = make_channel([]).model_copy(update={"data_source": "demo"})

        result = calculate_channel_analytics(channel_data)

        self.assertEqual(result.data_source, "demo")

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
        self.assertEqual(
            set(result.model_dump()), {"data_source", "channel", "videos"}
        )
        self.assertEqual(result.data_source, "youtube_api")
        openapi = app.openapi()
        original_endpoint = openapi["paths"]["/api/youtube/channel"]["post"]
        response_schema = original_endpoint["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        self.assertEqual(response_schema["$ref"], "#/components/schemas/ChannelResponse")
        self.assertIsInstance(result, ChannelResponse)

    def test_analytics_endpoint_uses_shared_snapshot(self) -> None:
        channel_data = make_channel([make_video("sample", 100, 10, 5)])
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
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

    def test_analytics_snapshot_is_reused_and_preserves_real_data_source(self) -> None:
        channel_data = make_channel([make_video("sample", 100, 10, 5)])
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(return_value=channel_data),
        ) as get_channel_data:
            async def get_twice():
                first = await get_analytics_snapshot("https://youtube.com/@creator")
                second = await get_analytics_snapshot(
                    "https://www.youtube.com/@creator/"
                )
                return first, second

            first, second = asyncio.run(get_twice())

        get_channel_data.assert_awaited_once_with("https://youtube.com/@creator")
        self.assertEqual(first.data_source, "youtube_api")
        self.assertEqual(second.data_source, "youtube_api")
        self.assertEqual(second.analytics.total_recent_video_views, 100)

    def test_http_https_host_case_trailing_slash_and_page_suffixes_normalize(self) -> None:
        canonical_key = _cache_key("https://youtube.com/@creator")

        self.assertEqual(
            _cache_key("HTTP://WWW.YouTube.COM/@creator/videos/"),
            canonical_key,
        )
        self.assertEqual(
            _cache_key("https://m.youtube.com/@creator/shorts"),
            canonical_key,
        )
        self.assertEqual(
            _cache_key("https://youtube.com/@creator/streams/"),
            canonical_key,
        )
        self.assertEqual(_cache_key("https://youtube.com/@other"), "//youtube.com/@other")

    def test_channel_id_reuses_snapshot_fetched_by_handle(self) -> None:
        channel_data = make_channel([make_video("sample", 100, 10, 5)])
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(return_value=channel_data),
        ) as get_channel_data:
            async def fetch_by_handle_then_id():
                handle_snapshot = await get_analytics_snapshot(
                    "https://youtube.com/@creator"
                )
                id_snapshot = await get_analytics_snapshot(
                    "https://youtube.com/channel/channel-1/videos"
                )
                return handle_snapshot, id_snapshot

            handle_snapshot, id_snapshot = asyncio.run(fetch_by_handle_then_id())

        get_channel_data.assert_awaited_once()
        self.assertEqual(handle_snapshot.channel.channel_id, "channel-1")
        self.assertEqual(id_snapshot.channel.channel_id, "channel-1")

    def test_snapshot_reads_are_deep_copy_isolated(self) -> None:
        channel_data = make_channel([make_video("sample", 100, 10, 5)])
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(return_value=channel_data),
        ) as get_channel_data:
            async def mutate_then_read():
                first = await get_analytics_snapshot("https://youtube.com/@creator")
                first.channel.name = "Mutated"
                first.videos[0].title = "Mutated nested video"
                first.analytics.average_views_per_video = 999
                second = await get_analytics_snapshot("https://youtube.com/@creator")
                return second

            second = asyncio.run(mutate_then_read())

        get_channel_data.assert_awaited_once()
        self.assertEqual(second.channel.name, "Creator")
        self.assertEqual(second.videos[0].title, "Video sample")
        self.assertEqual(second.analytics.average_views_per_video, 100)

    def test_concurrent_snapshot_requests_share_one_youtube_fetch(self) -> None:
        channel_data = make_channel([make_video("sample", 100, 10, 5)])

        async def delayed_fetch(channel_url: str):
            await asyncio.sleep(0)
            return channel_data

        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(side_effect=delayed_fetch),
        ) as get_channel_data:
            async def get_concurrently():
                return await asyncio.gather(
                    get_analytics_snapshot("https://youtube.com/@creator"),
                    get_analytics_snapshot("https://www.youtube.com/@creator/"),
                )

            first, second = asyncio.run(get_concurrently())

        get_channel_data.assert_awaited_once()
        self.assertEqual(first.data_source, "youtube_api")
        self.assertEqual(second.data_source, "youtube_api")

    def test_analytics_snapshot_preserves_demo_data_source(self) -> None:
        channel_data = make_channel([]).model_copy(update={"data_source": "demo"})
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(return_value=channel_data),
        ):
            result = asyncio.run(
                get_analytics_snapshot("https://youtube.com/@demo")
            )

        self.assertEqual(result.data_source, "demo")

    def test_analytics_snapshot_expires_after_configured_ttl(self) -> None:
        channel_data = make_channel([])
        current_time = [100.0]
        with (
            patch(
                "backend.services.analytics_snapshot_service.get_channel_data",
                new=AsyncMock(return_value=channel_data),
            ) as get_channel_data,
            patch(
                "backend.services.analytics_snapshot_service.time.monotonic",
                side_effect=lambda: current_time[0],
            ),
        ):
            async def fetch_then_expire():
                first = await get_analytics_snapshot("https://youtube.com/@creator")
                current_time[0] += 301
                second = await get_analytics_snapshot("https://youtube.com/@creator")
                return first, second

            asyncio.run(fetch_then_expire())

        self.assertEqual(get_channel_data.await_count, 2)

    def test_failed_analytics_snapshot_is_not_cached(self) -> None:
        channel_data = make_channel([])
        api_error = YouTubeServiceError("YouTube API is unavailable.", 502)
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(side_effect=[api_error, channel_data]),
        ) as get_channel_data:
            async def retry_after_failure():
                with self.assertRaises(YouTubeServiceError):
                    await get_analytics_snapshot("https://youtube.com/@creator")
                return await get_analytics_snapshot("https://youtube.com/@creator")

            result = asyncio.run(retry_after_failure())

        self.assertEqual(result.data_source, "youtube_api")
        self.assertEqual(get_channel_data.await_count, 2)

    def test_concurrent_waiters_all_receive_shared_fetch_exception(self) -> None:
        api_error = YouTubeServiceError("YouTube API is unavailable.", 502)
        fetch_started = asyncio.Event()
        allow_failure = asyncio.Event()

        async def fail_after_both_waiters_join(_channel_url: str):
            fetch_started.set()
            await allow_failure.wait()
            raise api_error

        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(side_effect=fail_after_both_waiters_join),
        ) as get_channel_data:
            async def await_shared_failure():
                first = asyncio.create_task(
                    get_analytics_snapshot("https://youtube.com/@creator")
                )
                await fetch_started.wait()
                second = asyncio.create_task(
                    get_analytics_snapshot("https://youtube.com/@creator")
                )
                await asyncio.sleep(0)
                allow_failure.set()
                return await asyncio.gather(first, second, return_exceptions=True)

            results = asyncio.run(await_shared_failure())

        get_channel_data.assert_awaited_once()
        self.assertEqual(results, [api_error, api_error])

    def test_cache_evicts_oldest_entry_over_capacity(self) -> None:
        channel_data = make_channel([])

        async def fetch_requested_channel(channel_url: str):
            requested_id = channel_url.rsplit("/", 1)[-1]
            return channel_data.model_copy(
                update={
                    "channel": channel_data.channel.model_copy(
                        update={"channel_id": requested_id}
                    )
                }
            )

        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(side_effect=fetch_requested_channel),
        ) as get_channel_data:
            async def fill_and_check_capacity():
                for index in range(MAX_ANALYTICS_SNAPSHOTS + 1):
                    await get_analytics_snapshot(
                        f"https://youtube.com/channel/channel-{index}"
                    )
                await get_analytics_snapshot("https://youtube.com/channel/channel-0")
                await get_analytics_snapshot(
                    f"https://youtube.com/channel/channel-{MAX_ANALYTICS_SNAPSHOTS}"
                )

            asyncio.run(fill_and_check_capacity())

        self.assertEqual(get_channel_data.await_count, MAX_ANALYTICS_SNAPSHOTS + 2)

    def test_cancelled_waiters_do_not_cancel_failed_fetch_or_leak_task(self) -> None:
        api_error = YouTubeServiceError("YouTube API is unavailable.", 502)
        channel_data = make_channel([])
        fetch_started = asyncio.Event()
        allow_failure = asyncio.Event()
        loop_errors: list[dict[str, object]] = []

        async def fail_after_waiter_cancellation(_channel_url: str):
            fetch_started.set()
            await allow_failure.wait()
            raise api_error

        fetch_count = 0

        async def fail_once_then_succeed(channel_url: str):
            nonlocal fetch_count
            fetch_count += 1
            if fetch_count == 1:
                return await fail_after_waiter_cancellation(channel_url)
            return channel_data

        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(side_effect=fail_once_then_succeed),
        ) as get_channel_data:
            async def cancel_all_waiters_then_retry():
                loop = asyncio.get_running_loop()
                loop.set_exception_handler(lambda _loop, context: loop_errors.append(context))
                waiter = asyncio.create_task(
                    get_analytics_snapshot("https://youtube.com/@creator")
                )
                await fetch_started.wait()
                second_waiter = asyncio.create_task(
                    get_analytics_snapshot("https://youtube.com/@creator")
                )
                await asyncio.sleep(0)
                waiter.cancel()
                second_waiter.cancel()
                results = await asyncio.gather(
                    waiter, second_waiter, return_exceptions=True
                )
                self.assertTrue(
                    all(isinstance(result, asyncio.CancelledError) for result in results)
                )
                allow_failure.set()
                for _ in range(10):
                    if not analytics_snapshot_service._inflight:
                        break
                    await asyncio.sleep(0)
                self.assertFalse(analytics_snapshot_service._inflight)
                return await get_analytics_snapshot("https://youtube.com/@creator")

            result = asyncio.run(cancel_all_waiters_then_retry())

        self.assertEqual(result.data_source, "youtube_api")
        self.assertEqual(get_channel_data.await_count, 2)
        self.assertEqual(loop_errors, [])

    def test_invalid_channel_url_is_rejected_before_fetching(self) -> None:
        with patch(
            "backend.services.analytics_snapshot_service.get_channel_data",
            new=AsyncMock(),
        ) as get_channel_data:
            with self.assertRaises(YouTubeServiceError) as error:
                asyncio.run(get_analytics_snapshot("https://example.com/@creator"))

        self.assertEqual(error.exception.status_code, 422)
        get_channel_data.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
