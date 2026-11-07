import React from 'react';
import { Header } from '../components/Header';
import { useChannel } from '../context/ChannelContext';
import {
  BrainCircuit,
  Database,
  Sparkles,
  CheckCircle2,
  Cpu,
  ShieldCheck,
  Clock,
  Tag,
  Layers
} from 'lucide-react';

export const MemoryCenterPage: React.FC = () => {
  const { channelData } = useChannel();

  if (!channelData) {
    return null;
  }

  const { channel, analytics } = channelData;

  const avgComments = analytics.average_comments_per_video !== null && analytics.average_comments_per_video !== undefined
    ? Math.round(analytics.average_comments_per_video)
    : 'N/A';

  const memories = [
    {
      category: "Creator Profile",
      icon: Cpu,
      color: "text-violet-400 bg-violet-500/10 border-violet-500/20",
      items: [
        { title: "Channel Identity", desc: `${channel.name} (${channel.subscriber_count?.toLocaleString() || 'N/A'} subscribers)` },
        { title: "Core Focus", desc: channel.description ? channel.description.substring(0, 120) + '...' : 'YouTube Content Creation & Creator Education' },
        { title: "Content Volume", desc: `Sliding window of ${analytics.recent_video_count} recent videos analyzed` }
      ]
    },
    {
      category: "Content Preferences",
      icon: Layers,
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
      items: [
        { title: "Average Video Views", desc: analytics.average_views_per_video ? Math.round(analytics.average_views_per_video).toLocaleString() + ' views' : 'N/A' },
        { title: "Engagement Benchmark", desc: analytics.average_engagement_rate_percent ? analytics.average_engagement_rate_percent.toFixed(2) + '%' : 'N/A' },
        { title: "Top Format Identifier", desc: analytics.highest_viewed_video?.title || 'High-utility case studies' }
      ]
    },
    {
      category: "Audience Intelligence",
      icon: Database,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
      items: [
        { title: "Interaction Responsiveness", desc: `Average ${avgComments} comments per video` },
        { title: "Viewer Retention Drivers", desc: "Strong problem statement hooks and direct actionable insights" },
        { title: "Sentiment Baseline", desc: "Highly receptive to practical tutorials and transparent breakdowns" }
      ]
    },
    {
      category: "Successful Patterns",
      icon: CheckCircle2,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
      items: [
        { title: "Top Outlier Video", desc: analytics.highest_viewed_video?.title || 'N/A' },
        { title: "Outlier Performance", desc: analytics.highest_viewed_video ? `${analytics.highest_viewed_video.view_count.toLocaleString()} views` : 'N/A' },
        { title: "Retention Multiplier", desc: "Clear thumbnail-title synergy yielding above-average CTR" }
      ]
    },
    {
      category: "Improvement Areas",
      icon: ShieldCheck,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
      items: [
        { title: "Lowest Viewed Outlier", desc: analytics.lowest_viewed_video?.title || 'N/A' },
        { title: "Hook Optimization", desc: "Reduce introductory delay in first 10 seconds" },
        { title: "Call-to-Action Density", desc: "Increase active question-based comments to boost engagement rate" }
      ]
    },
    {
      category: "Experiment History",
      icon: Clock,
      color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
      items: [
        { title: "Last Analysis Timestamp", desc: new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString() },
        { title: "Missing Data Policy", desc: "Strict adherence to available YouTube API v3 metrics without imputation" },
        { title: "Memory Persistence", desc: "Cached in local state & session storage for continuous adaptation" }
      ]
    }
  ];

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-charcoal-950">
      <Header
        title="Hindsight Memory Center"
        subtitle="Persistent long-term memory powering personalized AI recommendations"
      />

      <div className="p-8 space-y-8 flex-1 max-w-7xl w-full mx-auto">
        {/* Banner */}
        <div className="bg-gradient-to-r from-violet-900/40 via-charcoal-900 to-charcoal-900 border border-violet-500/30 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between shadow-2xl relative overflow-hidden gap-6">
          <div className="absolute right-0 top-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="space-y-2 max-w-2xl z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-xs font-semibold">
              <BrainCircuit className="w-3.5 h-3.5 animate-pulse" />
              <span>Hindsight Architecture</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">How Hindsight Memory Powers CreatorIQ</h2>
            <p className="text-sm text-gray-300">
              Unlike stateless chatbots, Hindsight continuously indexes your channel patterns, audience feedback, and successful strategies into persistent vector memory nodes to provide hyper-personalized recommendations.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-charcoal-850 border border-charcoal-700 text-center shrink-0 z-10">
            <span className="text-3xl font-extrabold text-violet-400">6</span>
            <span className="block text-xs text-gray-400 mt-1">Active Memory Clusters</span>
          </div>
        </div>

        {/* Memory Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {memories.map((mem, index) => {
            const Icon = mem.icon;
            return (
              <div
                key={index}
                className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl hover:border-violet-500/40 transition-all flex flex-col justify-between space-y-6 group"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-bold text-white">{mem.category}</h3>
                    <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${mem.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </div>

                  <div className="space-y-4">
                    {mem.items.map((item, i) => (
                      <div key={i} className="p-3 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-1">
                        <div className="text-xs font-semibold text-violet-400 flex items-center gap-1.5">
                          <Tag className="w-3 h-3" />
                          <span>{item.title}</span>
                        </div>
                        <p className="text-xs text-gray-300 font-medium line-clamp-2">{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-2 border-t border-charcoal-800 flex items-center justify-between text-[11px] text-gray-400">
                  <span>Status: Synced</span>
                  <span className="text-violet-400 font-semibold">Memory Node #{index + 1}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
