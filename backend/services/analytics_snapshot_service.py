"""Process-local analytics cache; entries are neither durable nor shared across workers."""

import asyncio
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from pydantic import ValidationError

from backend.schemas.analytics import AnalyticsChannelResponse
from backend.schemas.youtube import ChannelRequest
from backend.services.analytics_service import calculate_channel_analytics
from backend.services.youtube_service import YouTubeServiceError, get_channel_data

ANALYTICS_SNAPSHOT_TTL_SECONDS = 300
MAX_ANALYTICS_SNAPSHOTS = 128


@dataclass(frozen=True)
class _CachedSnapshot:
    snapshot: AnalyticsChannelResponse
    expires_at: float


_cache: dict[str, _CachedSnapshot] = {}
_inflight: dict[str, asyncio.Task[AnalyticsChannelResponse]] = {}
_channel_id_aliases: dict[str, str] = {}
_cache_lock = threading.Lock()


def _cache_key(channel_url: str) -> str:
    try:
        validated_url = ChannelRequest(channel_url=channel_url).channel_url
        parsed = urlsplit(validated_url)
    except (ValidationError, ValueError) as exc:
        raise YouTubeServiceError("Provide a valid YouTube channel URL.", 422) from exc

    segments = [segment for segment in parsed.path.split("/") if segment]
    if segments[0].startswith("@"):
        channel_path = f"/{segments[0]}"
    else:
        channel_path = f"/{segments[0]}/{segments[1]}"

    return urlunsplit(("", "youtube.com", channel_path, "", ""))


def _copy_snapshot(snapshot: AnalyticsChannelResponse) -> AnalyticsChannelResponse:
    return snapshot.model_copy(deep=True)


def _remove_inflight(
    key: str, task: asyncio.Task[AnalyticsChannelResponse]
) -> None:
    with _cache_lock:
        if _inflight.get(key) is task:
            _inflight.pop(key)
    if not task.cancelled():
        task.exception()


def _remove_cache_entry(key: str) -> None:
    _cache.pop(key, None)
    for channel_id, alias_key in list(_channel_id_aliases.items()):
        if alias_key == key:
            _channel_id_aliases.pop(channel_id, None)


def _cached_snapshot(
    key: str, now: float
) -> AnalyticsChannelResponse | None:
    candidate_key = key
    segments = [segment for segment in urlsplit(key).path.split("/") if segment]
    if len(segments) == 2 and segments[0] == "channel":
        candidate_key = _channel_id_aliases.get(segments[1], key)

    cached = _cache.get(candidate_key)
    if cached is None:
        return None
    if cached.expires_at <= now:
        _remove_cache_entry(candidate_key)
        return None
    return _copy_snapshot(cached.snapshot)


async def _fetch_and_cache_snapshot(
    channel_url: str, key: str
) -> AnalyticsChannelResponse:
    channel_data = await get_channel_data(channel_url)
    snapshot = calculate_channel_analytics(channel_data)

    with _cache_lock:
        _cache[key] = _CachedSnapshot(
            snapshot=_copy_snapshot(snapshot),
            expires_at=time.monotonic() + ANALYTICS_SNAPSHOT_TTL_SECONDS,
        )
        _channel_id_aliases[snapshot.channel.channel_id] = key
        if len(_cache) > MAX_ANALYTICS_SNAPSHOTS:
            oldest_key = min(_cache, key=lambda cache_key: _cache[cache_key].expires_at)
            _remove_cache_entry(oldest_key)

    return snapshot


async def get_analytics_snapshot(channel_url: str) -> AnalyticsChannelResponse:
    key = _cache_key(channel_url)
    now = time.monotonic()
    with _cache_lock:
        cached_snapshot = _cached_snapshot(key, now)
        if cached_snapshot is not None:
            return cached_snapshot

        task = _inflight.get(key)
        if task is None:
            task = asyncio.create_task(_fetch_and_cache_snapshot(channel_url, key))
            _inflight[key] = task
            task.add_done_callback(lambda completed: _remove_inflight(key, completed))

    return _copy_snapshot(await asyncio.shield(task))


def _clear_analytics_snapshot_cache() -> None:
    with _cache_lock:
        _cache.clear()
        _channel_id_aliases.clear()
        _inflight.clear()
