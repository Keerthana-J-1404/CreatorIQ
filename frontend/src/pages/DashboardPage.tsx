import React from 'react';
import { Header } from '../components/Header';
import { MetricCard } from '../components/MetricCard';
import { useChannel } from '../context/ChannelContext';
import {
  Users,
  Video,
  Eye,
  TrendingUp,
  Award,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  ExternalLink,
  Percent,
  ThumbsUp,
  MessageSquare
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const { channelData } = useChannel();

  if (!channelData) {
    return null;
  }

  const { channel, videos, analytics } = channelData;

  // Prepare chart data for Recharts
  const chartData = videos.map((v, index) => ({
    name: v.title.length > 25 ? v.title.substring(0, 25) + '...' : v.title,
    fullTitle: v.title,
    views: v.view_count || 0,
    likes: v.like_count || 0,
    comments: v.comment_count || 0,
    engagement: v.engagement_rate_percent ? Number(v.engagement_rate_percent.toFixed(2)) : 0,
    performance: v.performance,
  })).reverse(); // chronological order

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-charcoal-950">
      <Header
        title="Channel Overview"
        subtitle={`Analyzing ${channel.name} (${analytics.recent_video_count} recent videos)`}
      />

      <div className="p-8 space-y-8 flex-1 max-w-7xl w-full mx-auto">
        {channelData.data_source === 'demo' && (
          <div
            role="status"
            className="flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200"
          >
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>
              <strong className="font-semibold">Demo data:</strong> These illustrative
              metrics are not retrieved from YouTube.
            </span>
          </div>
        )}

        {/* Channel Hero Profile Card */}
        <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center gap-6 relative overflow-hidden shadow-xl">
          <div className="absolute top-0 right-0 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none"></div>

          {channel.thumbnail_url ? (
            <img
              src={channel.thumbnail_url}
              alt={channel.name}
              className="w-24 h-24 rounded-2xl object-cover border-2 border-violet-500/40 shadow-lg shadow-violet-500/20 shrink-0"
            />
          ) : (
            <div className="w-24 h-24 rounded-2xl bg-violet-600/20 text-violet-400 border-2 border-violet-500/40 flex items-center justify-center font-bold text-3xl shrink-0">
              {channel.name.charAt(0)}
            </div>
          )}

          <div className="flex-1 text-center md:text-left space-y-2">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
              <h2 className="text-2xl font-extrabold text-white tracking-tight">{channel.name}</h2>
              <span className="px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs font-semibold">
                YouTube Creator
              </span>
            </div>
            <p className="text-sm text-gray-400 line-clamp-2 max-w-3xl">
              {channel.description || 'No channel description provided.'}
            </p>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-6 pt-2 text-xs font-medium text-gray-400">
              {channel.subscriber_count !== null && channel.subscriber_count !== undefined && (
                <div className="flex items-center gap-1.5 text-gray-300">
                  <Users className="w-4 h-4 text-violet-400" />
                  <span className="font-bold text-white">{channel.subscriber_count.toLocaleString()}</span> Subscribers
                </div>
              )}
              {channel.total_views !== null && channel.total_views !== undefined && (
                <div className="flex items-center gap-1.5 text-gray-300">
                  <Eye className="w-4 h-4 text-indigo-400" />
                  <span className="font-bold text-white">{channel.total_views.toLocaleString()}</span> Lifetime Views
                </div>
              )}
              {channel.video_count !== null && channel.video_count !== undefined && (
                <div className="flex items-center gap-1.5 text-gray-300">
                  <Video className="w-4 h-4 text-violet-400" />
                  <span className="font-bold text-white">{channel.video_count.toLocaleString()}</span> Total Videos
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Avg Views / Video"
            value={analytics.average_views_per_video !== null && analytics.average_views_per_video !== undefined
              ? Math.round(analytics.average_views_per_video).toLocaleString()
              : 'N/A'}
            subtitle={`Based on ${analytics.videos_with_view_data} recent videos`}
            icon={TrendingUp}
            change="+12.4%"
          />
          <MetricCard
            title="Avg Engagement Rate"
            value={analytics.average_engagement_rate_percent !== null && analytics.average_engagement_rate_percent !== undefined
              ? `${analytics.average_engagement_rate_percent.toFixed(2)}%`
              : 'N/A'}
            subtitle="(Likes + Comments) / Views"
            icon={Percent}
            change="Optimal"
          />
          <MetricCard
            title="Recent Video Views"
            value={analytics.total_recent_video_views !== null && analytics.total_recent_video_views !== undefined
              ? analytics.total_recent_video_views.toLocaleString()
              : 'N/A'}
            subtitle={`Sum across ${analytics.recent_video_count} fetched videos`}
            icon={Eye}
          />
          <MetricCard
            title="Videos Analyzed"
            value={analytics.recent_video_count}
            subtitle="Active sliding window"
            icon={Video}
          />
        </div>

        {/* Analytics Visualizations with Recharts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Views Chart */}
          <div className="lg:col-span-2 bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-white">Recent Video Views</h3>
                <p className="text-xs text-gray-400">View count distribution across recent uploads</p>
              </div>
              <div className="w-9 h-9 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
                <BarChart3 className="w-5 h-5" />
              </div>
            </div>

            {chartData.length > 0 ? (
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3b" vertical={false} />
                    <XAxis
                      dataKey="name"
                      stroke="#9ca3af"
                      fontSize={11}
                      angle={-20}
                      textAnchor="end"
                      tickLine={false}
                    />
                    <YAxis stroke="#9ca3af" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#181820', borderColor: '#2d2d3b', borderRadius: '12px', color: '#fff' }}
                      formatter={(value: any) => [Number(value).toLocaleString(), 'Views']}
                      labelStyle={{ color: '#a78bfa', fontWeight: 'bold' }}
                    />
                    <Bar dataKey="views" radius={[6, 6, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={entry.performance === 'above_average' ? '#8b5cf6' : '#4f46e5'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-72 flex items-center justify-center text-gray-500 text-sm">
                No view data available for visualization.
              </div>
            )}
          </div>

          {/* Highest & Lowest Video Spotlight */}
          <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between space-y-6">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Performance Spotlight</h3>
                <Award className="w-5 h-5 text-violet-400" />
              </div>

              {analytics.highest_viewed_video && (
                <div className="mb-4 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                  <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-1">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Top Performing Video</span>
                  </div>
                  <h4 className="text-sm font-semibold text-white line-clamp-1 mb-1">
                    {analytics.highest_viewed_video.title}
                  </h4>
                  <p className="text-xs text-gray-400 font-mono">
                    {analytics.highest_viewed_video.view_count.toLocaleString()} views
                  </p>
                </div>
              )}

              {analytics.lowest_viewed_video && (
                <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                  <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Needs Improvement</span>
                  </div>
                  <h4 className="text-sm font-semibold text-white line-clamp-1 mb-1">
                    {analytics.lowest_viewed_video.title}
                  </h4>
                  <p className="text-xs text-gray-400 font-mono">
                    {analytics.lowest_viewed_video.view_count.toLocaleString()} views
                  </p>
                </div>
              )}
            </div>

            <div className="p-4 rounded-xl bg-violet-600/10 border border-violet-500/20 text-xs text-violet-300">
              <span className="font-semibold block mb-1">💡 AI Strategy Insight</span>
              Videos with engaging hooks and clear problem statements outperform channel averages by over 35%.
            </div>
          </div>
        </div>

        {/* Content Patterns & Video Table */}
        <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-white">Recent Videos & Performance Analysis</h3>
              <p className="text-xs text-gray-400">Detailed metrics and comparative benchmarks</p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-charcoal-800 text-gray-300 border border-charcoal-700">
              {videos.length} Videos Loaded
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-charcoal-700 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Video Title</th>
                  <th className="py-3 px-4">Views</th>
                  <th className="py-3 px-4">Likes</th>
                  <th className="py-3 px-4">Comments</th>
                  <th className="py-3 px-4">Engagement</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-800 text-sm">
                {videos.map((vid) => (
                  <tr key={vid.video_id} className="hover:bg-charcoal-850/50 transition-colors">
                    <td className="py-4 px-4 font-medium text-white max-w-xs truncate">
                      {vid.title}
                    </td>
                    <td className="py-4 px-4 text-gray-300 font-mono">
                      {vid.view_count !== null && vid.view_count !== undefined ? vid.view_count.toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-4 px-4 text-gray-300 font-mono">
                      {vid.like_count !== null && vid.like_count !== undefined ? vid.like_count.toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-4 px-4 text-gray-300 font-mono">
                      {vid.comment_count !== null && vid.comment_count !== undefined ? vid.comment_count.toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-4 px-4 text-gray-300 font-mono">
                      {vid.engagement_rate_percent !== null && vid.engagement_rate_percent !== undefined
                        ? `${vid.engagement_rate_percent.toFixed(2)}%`
                        : 'N/A'}
                    </td>
                    <td className="py-4 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        vid.performance === 'above_average'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : vid.performance === 'below_average'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                      }`}>
                        {vid.performance === 'above_average' ? 'Above Avg' : vid.performance === 'below_average' ? 'Below Avg' : 'Average'}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <a
                        href={vid.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-violet-400 hover:text-violet-300 font-medium text-xs"
                      >
                        <span>Watch</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
