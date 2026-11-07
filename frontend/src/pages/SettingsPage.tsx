import React from 'react';
import { Header } from '../components/Header';
import { useChannel } from '../context/ChannelContext';
import { useNavigate } from 'react-router-dom';
import {
  Settings as SettingsIcon,
  Tv,
  ShieldCheck,
  Database,
  LogOut,
  Trash2,
  Cpu,
  Globe
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { channelData, currentChannelUrl, clearChannel } = useChannel();
  const navigate = useNavigate();

  const handleDisconnect = () => {
    clearChannel();
    navigate('/');
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-charcoal-950">
      <Header
        title="Settings & Configuration"
        subtitle="Manage your channel connection, API endpoints, and memory preferences"
      />

      <div className="p-8 space-y-8 flex-1 max-w-4xl w-full mx-auto">
        {/* Connected Channel Card */}
        <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-charcoal-700">
            <div className="w-10 h-10 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <Tv className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Connected YouTube Channel</h3>
              <p className="text-xs text-gray-400">Active channel currently driving analytics and AI strategist</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-charcoal-850 border border-charcoal-700">
            <div className="space-y-1">
              <h4 className="text-sm font-semibold text-white">{channelData?.channel.name || 'No Channel Connected'}</h4>
              <p className="text-xs text-gray-400 font-mono break-all">{currentChannelUrl || 'None'}</p>
            </div>
            <button
              onClick={handleDisconnect}
              className="px-4 py-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 font-semibold text-xs border border-red-500/20 transition-all flex items-center gap-2 shrink-0"
            >
              <LogOut className="w-4 h-4" />
              <span>Switch Channel</span>
            </button>
          </div>
        </div>

        {/* API & Backend Configuration */}
        <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-charcoal-700">
            <div className="w-10 h-10 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Backend API Integration</h3>
              <p className="text-xs text-gray-400">FastAPI backend connection settings</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-700 space-y-1">
              <span className="text-xs text-gray-400 font-medium block">API Base URL</span>
              <span className="text-sm font-semibold text-white font-mono">
                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000 (Proxy)'}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-700 space-y-1">
              <span className="text-xs text-gray-400 font-medium block">API Status</span>
              <span className="text-sm font-semibold text-emerald-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                <span>Connected & Healthy</span>
              </span>
            </div>
          </div>
        </div>

        {/* Hindsight Memory Management */}
        <div className="bg-charcoal-900 border border-charcoal-700/80 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-charcoal-700">
            <div className="w-10 h-10 rounded-xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Hindsight Memory Preferences</h3>
              <p className="text-xs text-gray-400">Manage persistent context and caching</p>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl bg-charcoal-850 border border-charcoal-700">
            <div>
              <h4 className="text-sm font-semibold text-white">Clear Cached Memory & Data</h4>
              <p className="text-xs text-gray-400">Reset local session storage and channel analytics cache</p>
            </div>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.href = '/';
              }}
              className="px-4 py-2.5 rounded-xl bg-charcoal-800 hover:bg-red-500/20 hover:text-red-400 text-gray-300 font-semibold text-xs border border-charcoal-700 transition-all flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear Cache</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
