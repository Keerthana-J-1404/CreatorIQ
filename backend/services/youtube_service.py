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


async def get_channel_data(channel_url: str) -> ChannelResponse:
    if not YOUTUBE_API_KEY:
        raise YouTubeServiceError("YouTube API is not configured.", 503)

    # Validate direct service calls as well as requests entering through FastAPI.
    try:
        validated_url = ChannelRequest(channel_url=channel_url).channel_url
    except ValidationError as exc:
        raise YouTubeServiceError("Provide a valid YouTube channel URL.", 422) from exc

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
        raise YouTubeServiceError("YouTube channel was not found.", 404)

    channel = channel_items[0]
    snippet = channel.get("snippet") or {}
    statistics = channel.get("statistics") or {}
    content_details = channel.get("contentDetails") or {}
    uploads = (content_details.get("relatedPlaylists") or {}).get("uploads")
    channel_id = channel.get("id")
    if not isinstance(channel_id, str):
        raise YouTubeServiceError("YouTube returned an invalid channel.", 502)

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

    return ChannelResponse(channel=channel_info, videos=videos)
