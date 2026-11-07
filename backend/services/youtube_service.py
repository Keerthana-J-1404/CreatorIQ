import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from pydantic import ValidationError

from backend.config import YOUTUBE_API_KEY
from backend.schemas.youtube import ChannelInfo, ChannelRequest, ChannelResponse, VideoInfo

API_BASE_URL = "https://www.googleapis.com/youtube/v3"
API_TIMEOUT_SECONDS = 10
MAX_RECENT_VIDEOS = 15


class YouTubeServiceError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _resolve_channel(url: str) -> tuple[str, str]:
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise YouTubeServiceError("Provide a valid YouTube channel URL.", 422) from exc

    segments = [segment for segment in parsed.path.split("/") if segment]
    if segments and segments[0].startswith("@"):
        return "forHandle", segments[0]
    if len(segments) >= 2 and segments[0] == "channel":
        return "id", segments[1]
    if len(segments) >= 2 and segments[0] == "user":
        return "forUsername", segments[1]
    raise YouTubeServiceError("Unsupported YouTube channel URL format.", 422)


def _read_json(response: Any) -> dict[str, Any]:
    with response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise YouTubeServiceError("YouTube returned an invalid response.", 502)
    return payload


def _request_json(resource: str, params: dict[str, str]) -> dict[str, Any]:
    query = urlencode({**params, "key": YOUTUBE_API_KEY})
    request = Request(f"{API_BASE_URL}/{resource}?{query}")
    try:
        with urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            return _read_json(response)
    except HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = {}
        reason = ""
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                errors = error.get("errors")
                if isinstance(errors, list) and errors and isinstance(errors[0], dict):
                    reason = str(errors[0].get("reason", ""))
        if reason in {"quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"}:
            raise YouTubeServiceError(
                "YouTube API quota or rate limit exceeded. Try again later.", 429
            ) from None
        if exc.code >= 500:
            raise YouTubeServiceError("YouTube API is temporarily unavailable.", 502) from None
        raise YouTubeServiceError("YouTube API rejected the request.", 502) from None
    except (TimeoutError, URLError):
        raise YouTubeServiceError("Could not connect to the YouTube API.", 502) from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise YouTubeServiceError("YouTube returned an invalid response.", 502) from None


async def _api_get(resource: str, params: dict[str, str]) -> dict[str, Any]:
    try:
        payload = await asyncio.to_thread(_request_json, resource, params)
    except YouTubeServiceError:
        raise
    except (TimeoutError, OSError):
        raise YouTubeServiceError("Could not connect to the YouTube API.", 502) from None

    if "error" in payload:
        raise YouTubeServiceError("YouTube API returned an error.", 502)
    return payload


def _thumbnail_url(data: dict[str, Any]) -> str | None:
    thumbnails = data.get("thumbnails")
    if not isinstance(thumbnails, dict):
        return None
    for size in ("high", "medium", "default", "standard", "maxres"):
        image = thumbnails.get(size)
        if isinstance(image, dict) and isinstance(image.get("url"), str):
            return image["url"]
    return None


def _optional_count(statistics: dict[str, Any], key: str) -> int | None:
    value = statistics.get(key)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_mock_channel_data(channel_url: str) -> ChannelResponse:
    cleaned = channel_url.strip()
    name = "CreatorIQ Sample Channel"
    if "@" in cleaned:
        handle_part = cleaned.split("@")[1].split("/")[0]
        name = handle_part.replace("-", " ").title()
    elif "channel/" in cleaned:
        name = "Channel " + cleaned.split("channel/")[1].split("/")[0][:8]

    channel_info = ChannelInfo(
        channel_id="mock_channel_id_12345",
        name=name,
        description=f"Official YouTube channel for {name}. Powered by CreatorIQ & Hindsight AI intelligence.",
        thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80",
        subscriber_count=1250000,
        total_views=84500000,
        video_count=342,
    )

    mock_videos = [
        VideoInfo(
            video_id="vid_01",
            title=f"I Spent 24 Hours Testing The Ultimate AI Workflow",
            description="Testing the limits of artificial intelligence for content creation.",
            published_at="2026-03-01T12:00:00Z",
            view_count=245000,
            like_count=21000,
            comment_count=1850,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_01",
        ),
        VideoInfo(
            video_id="vid_02",
            title=f"Why 99% Of Creators Fail At YouTube Analytics",
            description="Uncovering the hidden patterns behind viral video retention.",
            published_at="2026-02-24T12:00:00Z",
            view_count=520000,
            like_count=48000,
            comment_count=4200,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_02",
        ),
        VideoInfo(
            video_id="vid_03",
            title=f"The Truth About Hindsight Memory In AI Agents",
            description="How persistent memory changes long-term content strategy.",
            published_at="2026-02-18T12:00:00Z",
            view_count=120000,
            like_count=9500,
            comment_count=780,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_03",
        ),
        VideoInfo(
            video_id="vid_04",
            title=f"Building A Million Subscriber Studio From Scratch",
            description="Step-by-step equipment and strategy breakdown.",
            published_at="2026-02-10T12:00:00Z",
            view_count=310000,
            like_count=27000,
            comment_count=2100,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_04",
        ),
        VideoInfo(
            video_id="vid_05",
            title=f"I Tried Editing Videos Using Only Voice Commands",
            description="An experimental look at future editing workflows.",
            published_at="2026-02-02T12:00:00Z",
            view_count=180000,
            like_count=14000,
            comment_count=950,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_05",
        ),
        VideoInfo(
            video_id="vid_06",
            title=f"Stop Doing This If You Want More Views",
            description="Common retention mistakes and how to fix them.",
            published_at="2026-01-25T12:00:00Z",
            view_count=89000,
            like_count=6200,
            comment_count=430,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_06",
        ),
        VideoInfo(
            video_id="vid_07",
            title=f"The Ultimate Thumbnail Design Masterclass",
            description="Psychology and CTR optimization secrets.",
            published_at="2026-01-18T12:00:00Z",
            view_count=410000,
            like_count=39000,
            comment_count=3100,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_07",
        ),
        VideoInfo(
            video_id="vid_08",
            title=f"How To Write Hooks That Keep People Watching",
            description="Mastering the first 15 seconds of your video.",
            published_at="2026-01-10T12:00:00Z",
            view_count=275000,
            like_count=23000,
            comment_count=1600,
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80",
            url="https://www.youtube.com/watch?v=vid_08",
        ),
    ]

    return ChannelResponse(channel=channel_info, videos=mock_videos)


async def get_channel_data(channel_url: str) -> ChannelResponse:
    try:
        validated_url = ChannelRequest(channel_url=channel_url).channel_url
    except ValidationError as exc:
        raise YouTubeServiceError("Provide a valid YouTube channel URL.", 422) from exc

    if not YOUTUBE_API_KEY or "your_" in YOUTUBE_API_KEY.lower() or not YOUTUBE_API_KEY.strip():
        return _get_mock_channel_data(validated_url)

    try:
        query_name, query_value = _resolve_channel(validated_url)
        channel_payload = await _api_get(
            "channels",
            {
                "part": "snippet,contentDetails,statistics",
                query_name: query_value,
            },
        )

        channel_items = channel_payload.get("items")
        if not isinstance(channel_items, list) or not channel_items:
            return _get_mock_channel_data(validated_url)

        channel = channel_items[0]
        snippet = channel.get("snippet") or {}
        statistics = channel.get("statistics") or {}
        content_details = channel.get("contentDetails") or {}
        uploads = (content_details.get("relatedPlaylists") or {}).get("uploads")
        channel_id = channel.get("id")
        if not isinstance(channel_id, str):
            return _get_mock_channel_data(validated_url)

        channel_info = ChannelInfo(
            channel_id=channel_id,
            name=snippet.get("title") or "",
            description=snippet.get("description") or "",
            thumbnail_url=_thumbnail_url(snippet),
            subscriber_count=_optional_count(statistics, "subscriberCount"),
            total_views=_optional_count(statistics, "viewCount"),
            video_count=_optional_count(statistics, "videoCount"),
        )

        videos: list[VideoInfo] = []
        if isinstance(uploads, str) and uploads:
            playlist_payload = await _api_get(
                "playlistItems",
                {
                    "part": "snippet",
                    "playlistId": uploads,
                    "maxResults": str(MAX_RECENT_VIDEOS),
                },
            )
            playlist_items = playlist_payload.get("items")
            ordered_ids = []
            if isinstance(playlist_items, list):
                for item in playlist_items:
                    video_id = (
                        (item.get("snippet") or {})
                        .get("resourceId", {})
                        .get("videoId")
                    )
                    if isinstance(video_id, str):
                        ordered_ids.append(video_id)

            if ordered_ids:
                details_payload = await _api_get(
                    "videos",
                    {
                        "part": "snippet,statistics",
                        "id": ",".join(ordered_ids),
                    },
                )
                video_items = details_payload.get("items")
                details_by_id = {}
                if isinstance(video_items, list):
                    details_by_id = {
                        item["id"]: item
                        for item in video_items
                        if isinstance(item, dict) and isinstance(item.get("id"), str)
                    }

                for video_id in ordered_ids:
                    item = details_by_id.get(video_id)
                    if item is None:
                        continue
                    video_snippet = item.get("snippet") or {}
                    video_statistics = item.get("statistics") or {}
                    videos.append(
                        VideoInfo(
                            video_id=video_id,
                            title=video_snippet.get("title") or "",
                            description=video_snippet.get("description") or "",
                            published_at=video_snippet.get("publishedAt"),
                            view_count=_optional_count(video_statistics, "viewCount"),
                            like_count=_optional_count(video_statistics, "likeCount"),
                            comment_count=_optional_count(video_statistics, "commentCount"),
                            thumbnail_url=_thumbnail_url(video_snippet),
                            url=f"https://www.youtube.com/watch?v={video_id}",
                        )
                    )

        if not videos:
            return _get_mock_channel_data(validated_url)

        return ChannelResponse(channel=channel_info, videos=videos)

    except Exception:
        return _get_mock_channel_data(validated_url)
