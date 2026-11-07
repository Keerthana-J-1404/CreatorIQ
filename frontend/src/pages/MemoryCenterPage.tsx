import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { useChannel } from '../context/ChannelContext';
import { getChannelMemories } from '../services/api';
import {
  BrainCircuit,
  Database,
  CheckCircle2,
  Cpu,
  ShieldCheck,
  Clock,
  Tag,
  Layers,
  Loader2
} from 'lucide-react';

export const MemoryCenterPage: React.FC = () => {
  const { channelData } = useChannel();
  const channelId = channelData?.channel.channel_id || 'default_channel';

  const [memoryData, setMemoryData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    getChannelMemories(channelId)
      .then(res => {
        if (isMounted) {
          setMemoryData(res);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [channelId]);

  if (!channelData) {
    return null;
  }

  const icons = [Cpu, Layers, Database, CheckCircle2, ShieldCheck, Clock];
  const colors = [
    "text-violet-400 bg-violet-500/10 border-violet-500/20",
    "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    "text-purple-400 bg-purple-500/10 border-purple-500/20",
    "text-amber-400 bg-amber-500/10 border-amber-500/20",
    "text-blue-400 bg-blue-500/10 border-blue-500/20"
  ];

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-charcoal-950">
      <Header
        title="Hindsight Memory Center"
        subtitle="Persistent vector memory powered by Vectorize Hindsight for personalized AI recommendations"
      />

      <div className="p-8 space-y-8 flex-1 max-w-7xl w-full mx-auto">
        {/* Banner */}
        <div className="bg-gradient-to-r from-violet-900/40 via-charcoal-900 to-charcoal-900 border border-violet-500/30 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between shadow-2xl relative overflow-hidden gap-6">
          <div className="absolute right-0 top-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="space-y-2 max-w-2xl z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-xs font-semibold">
              <BrainCircuit className="w-3.5 h-3.5 animate-pulse" />
              <span>Vectorize Hindsight Integration</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">How Hindsight Memory Powers CreatorIQ</h2>
            <p className="text-sm text-gray-300">
              Unlike stateless chatbots, Hindsight continuously indexes channel metrics, audience feedback, and conversation history into persistent vector memory nodes to make the AI strategist smarter with every interaction.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-charcoal-850 border border-charcoal-700 text-center shrink-0 z-10">
            <span className="text-3xl font-extrabold text-violet-400">
              {memoryData?.total_memories || 6}
            </span>
            <span className="block text-xs text-gray-400 mt-1">Active Memory Nodes</span>
          </div>
        </div>

        {loading ? (
          <div className="py-20 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-violet-500" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {memoryData?.clusters?.map((cluster: any, index: number) => {
              const Icon = icons[index % icons.length];
              const color = colors[index % colors.length];
              return (
                <div
                  key={index}
                  className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl hover:border-violet-500/40 transition-all flex flex-col justify-between space-y-6 group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-base font-bold text-white">{cluster.category}</h3>
                      <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${color}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                    </div>

                    <div className="space-y-4">
                      {cluster.items.map((item: any, i: number) => (
                        <div key={i} className="p-3 rounded-xl bg-charcoal-850 border border-charcoal-700/60 space-y-1">
                          <div className="text-xs font-semibold text-violet-400 flex items-center justify-between">
                            <span className="flex items-center gap-1.5">
                              <Tag className="w-3 h-3" />
                              <span>{item.title}</span>
                            </span>
                            <span className="text-[10px] text-gray-500">{item.timestamp}</span>
                          </div>
                          <p className="text-xs text-gray-300 font-medium">{item.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-charcoal-800 flex items-center justify-between text-[11px] text-gray-400">
                    <span>Status: {memoryData.hindsight_status}</span>
                    <span className="text-violet-400 font-semibold">Cluster #{index + 1}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
