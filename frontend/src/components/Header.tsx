import React from 'react';
import { Sparkles, BrainCircuit, ShieldCheck, RefreshCw } from 'lucide-react';
import { useChannel } from '../context/ChannelContext';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  const { channelData, currentChannelUrl, analyze, loading } = useChannel();

  const handleRefresh = async () => {
    if (currentChannelUrl) {
      try {
        await analyze(currentChannelUrl);
      } catch (err) {
        // handled in context
      }
    }
  };

  return (
    <header className="bg-charcoal-900/80 backdrop-blur-md border-b border-charcoal-700 sticky top-0 z-30 px-8 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Hindsight Memory Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-600/10 border border-violet-500/20 text-violet-400 text-xs font-medium">
          <BrainCircuit className="w-3.5 h-3.5 animate-pulse" />
          <span>Hindsight Active</span>
        </div>

        {/* API Status Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>API Connected</span>
        </div>

        {currentChannelUrl && (
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 text-gray-300 text-xs font-medium border border-charcoal-700 transition-all disabled:opacity-50"
            title="Refresh Channel Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-violet-400' : ''}`} />
            <span className="hidden sm:inline">Sync Data</span>
          </button>
        )}
      </div>
    </header>
  );
};
