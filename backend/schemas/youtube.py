from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, field_validator

DataSource = Literal["youtube_api", "demo"]


class ChannelRequest(BaseModel):
    channel_url: str

    @field_validator("channel_url")
    @classmethod
    def validate_channel_url(cls, value: str) -> str:
        value = value.strip()
        try:
            parsed = urlsplit(value)
            host = parsed.hostname
        except ValueError:
            host = None
            parsed = None

        if (
            parsed is None
            or parsed.scheme not in {"http", "https"}
            or host not in {"youtube.com", "www.youtube.com", "m.youtube.com"}
        ):
            raise ValueError("Provide a valid YouTube channel URL.")

        segments = [segment for segment in parsed.path.split("/") if segment]
        is_handle = bool(segments and segments[0].startswith("@") and len(segments[0]) > 1)
        is_id_or_username = (
            len(segments) >= 2
            and segments[0] in {"channel", "user"}
            and bool(segments[1])
        )
        if not (is_handle or is_id_or_username):
            raise ValueError(
                "Supported channel URLs use /@handle, /channel/CHANNEL_ID, "
                "or /user/USERNAME."
            )
        return value


class ChannelInfo(BaseModel):
    channel_id: str
    name: str
    description: str
    thumbnail_url: str | None = None
    subscriber_count: int | None = None
    total_views: int | None = None
    video_count: int | None = None


class VideoInfo(BaseModel):
    video_id: str
    title: str
    description: str
    published_at: str | None = None
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    thumbnail_url: str | None = None
    url: str


class ChannelResponse(BaseModel):
    data_source: DataSource
    channel: ChannelInfo
    videos: list[VideoInfo]
