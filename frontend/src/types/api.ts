export interface ChannelRequest {
  channel_url: string;
}

export interface ChannelInfo {
  channel_id: string;
  name: string;
  description: string;
  thumbnail_url?: string | null;
  subscriber_count?: number | null;
  total_views?: number | null;
  video_count?: number | null;
}

export interface VideoInfo {
  video_id: string;
  title: string;
  description: string;
  published_at?: string | null;
  view_count?: number | null;
  like_count?: number | null;
  comment_count?: number | null;
  thumbnail_url?: string | null;
  url: string;
}

export interface VideoAnalytics extends VideoInfo {
  engagement_rate_percent?: number | null;
  views_vs_average_percent?: number | null;
  performance: "above_average" | "below_average" | "at_average" | "unavailable";
}

export interface VideoRanking {
  video_id: string;
  title: string;
  view_count: number;
}

export interface ChannelAnalytics {
  average_views_per_video?: number | null;
  average_likes_per_video?: number | null;
  average_comments_per_video?: number | null;
  average_engagement_rate_percent?: number | null;
  total_recent_video_views?: number | null;
  highest_viewed_video?: VideoRanking | null;
  lowest_viewed_video?: VideoRanking | null;
  recent_video_count: number;
  videos_with_view_data: number;
  videos_with_like_data: number;
  videos_with_comment_data: number;
  videos_with_engagement_rate: number;
  missing_data_policy: string;
}

export interface AnalyticsChannelResponse {
  data_source: "youtube_api" | "demo";
  channel: ChannelInfo;
  videos: VideoAnalytics[];
  analytics: ChannelAnalytics;
}

export interface ChannelResponse {
  data_source: "youtube_api" | "demo";
  channel: ChannelInfo;
  videos: VideoInfo[];
}
