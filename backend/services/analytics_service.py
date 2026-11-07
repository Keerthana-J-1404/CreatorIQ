from backend.schemas.analytics import (
    AnalyticsChannelResponse,
    ChannelAnalytics,
    VideoAnalytics,
    VideoRanking,
)
from backend.schemas.youtube import ChannelResponse

MISSING_DATA_POLICY = (
    "Each average uses only videos with that statistic available; missing statistics "
    "are excluded, not counted as zero. Engagement rate requires views greater than "
    "zero plus both likes and comments. Videos with zero views or incomplete "
    "engagement statistics have no engagement rate. Totals sum available view "
    "counts and are null when no view counts are available. Rankings use only videos "
    "with available view counts."
)


def calculate_channel_analytics(channel_data: ChannelResponse) -> AnalyticsChannelResponse:
    videos_with_views = [
        video for video in channel_data.videos if video.view_count is not None
    ]
    videos_with_likes = [
        video for video in channel_data.videos if video.like_count is not None
    ]
    videos_with_comments = [
        video for video in channel_data.videos if video.comment_count is not None
    ]
    view_counts = [video.view_count for video in videos_with_views]
    average_views = (
        sum(view_counts) / len(view_counts) if view_counts else None
    )
    average_likes = (
        sum(video.like_count for video in videos_with_likes) / len(videos_with_likes)
        if videos_with_likes
        else None
    )
    average_comments = (
        sum(video.comment_count for video in videos_with_comments)
        / len(videos_with_comments)
        if videos_with_comments
        else None
    )

    video_analytics: list[VideoAnalytics] = []
    engagement_rates: list[float] = []
    for video in channel_data.videos:
        engagement_rate = None
        if (
            video.view_count is not None
            and video.view_count > 0
            and video.like_count is not None
            and video.comment_count is not None
        ):
            engagement_rate = (
                (video.like_count + video.comment_count) / video.view_count * 100
            )
            engagement_rates.append(engagement_rate)

        views_vs_average = None
        performance = "unavailable"
        if video.view_count is not None and average_views is not None:
            if average_views == 0:
                performance = "at_average"
            else:
                views_vs_average = (video.view_count - average_views) / average_views * 100
                if video.view_count > average_views:
                    performance = "above_average"
                elif video.view_count < average_views:
                    performance = "below_average"
                else:
                    performance = "at_average"

        video_analytics.append(
            VideoAnalytics(
                **video.model_dump(),
                engagement_rate_percent=engagement_rate,
                views_vs_average_percent=views_vs_average,
                performance=performance,
            )
        )

    highest_video = (
        max(videos_with_views, key=lambda video: video.view_count)
        if videos_with_views
        else None
    )
    lowest_video = (
        min(videos_with_views, key=lambda video: video.view_count)
        if videos_with_views
        else None
    )

    return AnalyticsChannelResponse(
        data_source=channel_data.data_source,
        channel=channel_data.channel,
        videos=video_analytics,
        analytics=ChannelAnalytics(
            average_views_per_video=average_views,
            average_likes_per_video=average_likes,
            average_comments_per_video=average_comments,
            average_engagement_rate_percent=(
                sum(engagement_rates) / len(engagement_rates)
                if engagement_rates
                else None
            ),
            total_recent_video_views=sum(view_counts) if view_counts else None,
            highest_viewed_video=(
                VideoRanking(
                    video_id=highest_video.video_id,
                    title=highest_video.title,
                    view_count=highest_video.view_count,
                )
                if highest_video
                else None
            ),
            lowest_viewed_video=(
                VideoRanking(
                    video_id=lowest_video.video_id,
                    title=lowest_video.title,
                    view_count=lowest_video.view_count,
                )
                if lowest_video
                else None
            ),
            recent_video_count=len(channel_data.videos),
            videos_with_view_data=len(videos_with_views),
            videos_with_like_data=len(videos_with_likes),
            videos_with_comment_data=len(videos_with_comments),
            videos_with_engagement_rate=len(engagement_rates),
            missing_data_policy=MISSING_DATA_POLICY,
        ),
    )
