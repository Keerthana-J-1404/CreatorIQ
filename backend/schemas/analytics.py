from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.youtube import ChannelInfo, VideoInfo


class VideoRanking(BaseModel):
    video_id: str
    title: str
    view_count: int


class VideoAnalytics(VideoInfo):
    engagement_rate_percent: float | None = None
    views_vs_average_percent: float | None = None
    performance: Literal["above_average", "below_average", "at_average", "unavailable"]


class ChannelAnalytics(BaseModel):
    average_views_per_video: float | None = Field(
        description="Mean of available recent-video view counts; unavailable counts are excluded."
    )
    average_likes_per_video: float | None = Field(
        description="Mean of available recent-video like counts; unavailable counts are excluded."
    )
    average_comments_per_video: float | None = Field(
        description="Mean of available recent-video comment counts; unavailable counts are excluded."
    )
    average_engagement_rate_percent: float | None = Field(
        description=(
            "Mean of per-video engagement rates for videos with views greater than zero "
            "and both likes and comments available."
        )
    )
    total_recent_video_views: int | None = Field(
        description=(
            "Sum of available view counts for retrieved recent videos; None if no view "
            "counts are available. This is not the channel's lifetime view count."
        )
    )
    highest_viewed_video: VideoRanking | None
    lowest_viewed_video: VideoRanking | None
    recent_video_count: int
    videos_with_view_data: int
    videos_with_like_data: int
    videos_with_comment_data: int
    videos_with_engagement_rate: int
    missing_data_policy: str


class AnalyticsChannelResponse(BaseModel):
    channel: ChannelInfo
    videos: list[VideoAnalytics]
    analytics: ChannelAnalytics
