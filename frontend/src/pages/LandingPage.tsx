import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, BrainCircuit, TrendingUp, ShieldCheck, ArrowRight, Tv, AlertCircle, Loader2 } from 'lucide-react';
import { useChannel } from '../context/ChannelContext';

export const LandingPage: React.FC = () => {
  const [urlInput, setUrlInput] = useState<string>('');
  const { analyze, loading, error, channelData } = useChannel();
  const navigate = useNavigate();

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;

    try {
      await analyze(urlInput.trim());
      navigate('/dashboard');
    } catch (err) {
      // error is handled in context
    }
  };

  const handleQuickDemo = async (demoUrl: string) => {
    setUrlInput(demoUrl);
    try {
      await analyze(demoUrl);
      navigate('/dashboard');
    } catch (err) {
      // error is handled in context
    }
  };

  return (
    <div className="min-h-screen bg-charcoal-950 text-gray-100 flex flex-col justify-between relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-tr from-violet-600/20 to-indigo-600/10 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Top Nav */}
      <header className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-gray-200 to-violet-400 bg-clip-text text-transparent">
            CreatorIQ
          </span>
        </div>

        {channelData && (
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm shadow-lg shadow-violet-600/30 transition-all"
          >
            <span>Go to Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </header>

      {/* Hero Section */}
      <div className="w-full max-w-5xl mx-auto px-6 py-12 lg:py-20 text-center z-10 flex-1 flex flex-col justify-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs font-semibold uppercase tracking-wider mb-8 mx-auto">
          <BrainCircuit className="w-4 h-4" />
          <span>Powered by Hindsight Long-Term Memory & AI</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Your audience has a pattern.{' '}
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-violet-600 bg-clip-text text-transparent">
            Let's find it.
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-10 font-normal">
          Your AI content strategist that learns what works for <span className="text-white font-semibold">YOUR</span> audience. Stop guessing. Start growing.
        </p>

        {/* URL Input Form */}
        <form onSubmit={handleAnalyze} className="max-w-2xl mx-auto w-full mb-6">
          <div className="flex flex-col sm:flex-row gap-3 p-2 bg-charcoal-900 border border-charcoal-700 rounded-2xl shadow-2xl focus-within:border-violet-500 transition-all">
            <div className="flex items-center gap-3 px-3 flex-1">
              <Tv className="w-5 h-5 text-violet-400 shrink-0" />
              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="Enter YouTube Channel URL (e.g. https://www.youtube.com/@mkbhd)"
                className="w-full bg-transparent text-white placeholder-gray-500 text-sm sm:text-base focus:outline-none"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !urlInput.trim()}
              className="px-6 py-3.5 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white font-semibold text-sm sm:text-base flex items-center justify-center gap-2 shadow-lg shadow-violet-600/30 transition-all shrink-0 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Analyze My Channel</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Error Banner */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-3 text-left">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Quick Demo Suggestions */}
        <div className="flex flex-wrap items-center justify-center gap-3 text-xs text-gray-400 mb-16">
          <span className="text-gray-400">Try popular channels:</span>
          <button
            type="button"
            onClick={() => handleQuickDemo('https://www.youtube.com/@mkbhd')}
            className="px-3 py-1.5 rounded-lg bg-charcoal-900 hover:bg-charcoal-800 border border-charcoal-700 text-gray-300 transition-all"
          >
            @mkbhd
          </button>
          <button
            type="button"
            onClick={() => handleQuickDemo('https://www.youtube.com/@veritasium')}
            className="px-3 py-1.5 rounded-lg bg-charcoal-900 hover:bg-charcoal-800 border border-charcoal-700 text-gray-300 transition-all"
          >
            @veritasium
          </button>
          <button
            type="button"
            onClick={() => handleQuickDemo('https://www.youtube.com/@fireship')}
            className="px-3 py-1.5 rounded-lg bg-charcoal-900 hover:bg-charcoal-800 border border-charcoal-700 text-gray-300 transition-all"
          >
            @fireship
          </button>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-5xl mx-auto">
          <div className="p-6 rounded-2xl bg-charcoal-900 border border-charcoal-700/80 hover:border-violet-500/40 transition-all">
            <div className="w-12 h-12 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400 mb-4">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Content Intelligence</h3>
            <p className="text-sm text-gray-400">
              Identify top performing patterns, engagement outliers, and exactly why certain videos outperform your average.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-charcoal-900 border border-charcoal-700/80 hover:border-violet-500/40 transition-all">
            <div className="w-12 h-12 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400 mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">AI Strategist</h3>
            <p className="text-sm text-gray-400">
              Chat directly with an AI content strategist trained on your actual channel statistics and historical video data.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-charcoal-900 border border-charcoal-700/80 hover:border-violet-500/40 transition-all">
            <div className="w-12 h-12 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400 mb-4">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Hindsight Memory</h3>
            <p className="text-sm text-gray-400">
              Persistent memory architecture that remembers your creator preferences, audience feedback, and experiment history.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="w-full max-w-7xl mx-auto px-6 py-6 border-t border-charcoal-800 text-center text-xs text-gray-400 z-10 flex items-center justify-between">
        <div>CreatorIQ © {new Date().getFullYear()} — Stop guessing. Start growing.</div>
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Secure YouTube API v3 Integration</span>
        </div>
      </footer>
    </div>
  );
};
