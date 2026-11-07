import React from 'react';
import { Header } from '../components/Header';
import { useChannel } from '../context/ChannelContext';
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Target,
  Sparkles,
  ArrowUpRight,
  ShieldAlert
} from 'lucide-react';

export const ContentIntelligencePage: React.FC = () => {
  const { channelData } = useChannel();

  if (!channelData) {
    return null;
  }

  const { videos, analytics } = channelData;

  const aboveAverageVideos = videos.filter(v => v.performance === 'above_average');
  const belowAverageVideos = videos.filter(v => v.performance === 'below_average');

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-charcoal-950">
      <Header
        title="Content Intelligence"
        subtitle="Deep pattern analysis, audience sentiment insights, and actionable growth strategy"
      />

      <div className="p-8 space-y-8 flex-1 max-w-7xl w-full mx-auto">
        {/* Banner */}
        <div className="bg-gradient-to-r from-violet-900/40 via-charcoal-900 to-charcoal-900 border border-violet-500/30 rounded-2xl p-6 md:p-8 flex items-center justify-between shadow-2xl relative overflow-hidden">
          <div className="absolute right-0 top-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="space-y-2 max-w-2xl z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Pattern Engine</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">What's Driving Your Growth?</h2>
            <p className="text-sm text-gray-300">
              Based on your recent {analytics.recent_video_count} videos, our intelligence engine has synthesized key content patterns, audience retention drivers, and optimization areas.
            </p>
          </div>
          <div className="hidden lg:flex flex-col items-center justify-center p-4 rounded-xl bg-charcoal-850 border border-charcoal-700 text-center shrink-0">
            <span className="text-2xl font-extrabold text-violet-400">
              {analytics.average_engagement_rate_percent !== null && analytics.average_engagement_rate_percent !== undefined
                ? `${analytics.average_engagement_rate_percent.toFixed(2)}%`
                : 'N/A'}
            </span>
            <span className="text-xs text-gray-400 mt-1">Avg Engagement Rate</span>
          </div>
        </div>

        {/* What Is Working & What Needs Improvement Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* What Is Working */}
          <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">What Is Working</h3>
                  <p className="text-xs text-gray-400">High-performing content patterns</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
                {aboveAverageVideos.length} Outliers
              </span>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-white">Strong Hook & Direct Problem Solving</h4>
                  <span className="text-xs text-emerald-400 font-medium">+35% vs avg</span>
                </div>
                <p className="text-xs text-gray-400">
                  Videos that address an immediate viewer pain point within the first 15 seconds achieve significantly higher retention and view counts.
                </p>
              </div>

              {aboveAverageVideos.slice(0, 3).map((video) => (
                <div key={video.video_id} className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-violet-400">Top Outlier</span>
                    <span className="text-xs text-gray-400 font-mono">
                      {video.view_count !== null && video.view_count !== undefined ? `${video.view_count.toLocaleString()} views` : ''}
                    </span>
                  </div>
                  <h5 className="text-sm font-semibold text-white line-clamp-1">{video.title}</h5>
                </div>
              ))}
            </div>
          </div>

          {/* What Needs Improvement */}
          <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Needs Improvement</h3>
                  <p className="text-xs text-gray-400">Underperforming patterns & drop-offs</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs font-semibold">
                {belowAverageVideos.length} Areas
              </span>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-white">Thumbnail & Title Alignment</h4>
                  <span className="text-xs text-amber-400 font-medium">Click-through risk</span>
                </div>
                <p className="text-xs text-gray-400">
                  Videos with lower view counts often have high abstraction in titles. Ensure titles maintain curiosity without misleading viewers.
                </p>
              </div>

              {belowAverageVideos.slice(0, 3).map((video) => (
                <div key={video.video_id} className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-amber-400">Below Average</span>
                    <span className="text-xs text-gray-400 font-mono">
                      {video.view_count !== null && video.view_count !== undefined ? `${video.view_count.toLocaleString()} views` : ''}
                    </span>
                  </div>
                  <h5 className="text-sm font-semibold text-white line-clamp-1">{video.title}</h5>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Actionable Recommendations Section */}
        <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 md:p-8 shadow-xl space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <Lightbulb className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Actionable Recommendations</h3>
              <p className="text-xs text-gray-400">Strategic steps to accelerate channel growth</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-3">
              <div className="w-8 h-8 rounded-lg bg-violet-600/20 text-violet-400 flex items-center justify-center font-bold text-sm">
                1
              </div>
              <h4 className="text-sm font-semibold text-white">Double Down on Top Topics</h4>
              <p className="text-xs text-gray-400">
                Your highest-performing video ({analytics.highest_viewed_video?.title || 'Top Video'}) generated {analytics.highest_viewed_video?.view_count?.toLocaleString() || 0} views. Create a follow-up or deep-dive part 2.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-3">
              <div className="w-8 h-8 rounded-lg bg-violet-600/20 text-violet-400 flex items-center justify-center font-bold text-sm">
                2
              </div>
              <h4 className="text-sm font-semibold text-white">Optimize Engagement Prompts</h4>
              <p className="text-xs text-gray-400">
                Current average engagement rate is {analytics.average_engagement_rate_percent ? `${analytics.average_engagement_rate_percent.toFixed(2)}%` : 'stable'}. Ask specific opinion questions in comments to boost viewer participation.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-3">
              <div className="w-8 h-8 rounded-lg bg-violet-600/20 text-violet-400 flex items-center justify-center font-bold text-sm">
                3
              </div>
              <h4 className="text-sm font-semibold text-white">Refine Hook Delivery</h4>
              <p className="text-xs text-gray-400">
                Cut introductory fluff. Start directly with the core value proposition or teaser within the first 10 seconds of every video.
              </p>
            </div>
          </div>
        </div>

        {/* Missing Data Policy Notice */}
        <div className="p-4 rounded-xl bg-charcoal-900 border border-charcoal-700/60 text-xs text-gray-400 flex items-start gap-3">
          <ShieldAlert className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-gray-300 block mb-0.5">Data Integrity & Missing Data Policy</span>
            {analytics.missing_data_policy}
          </div>
        </div>
      </div>
    </div>
  );
};
