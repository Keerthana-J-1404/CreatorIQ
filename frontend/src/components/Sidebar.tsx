import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  BrainCircuit,
  MessageSquareCode,
  Database,
  Settings,
  LogOut,
  Sparkles,
  TrendingUp
} from 'lucide-react';
import { useChannel } from '../context/ChannelContext';

export const Sidebar: React.FC = () => {
  const { channelData, clearChannel } = useChannel();
  const navigate = useNavigate();

  const handleDisconnect = () => {
    clearChannel();
    navigate('/');
  };

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Content Intelligence', path: '/intelligence', icon: TrendingUp },
    { name: 'AI Strategist', path: '/strategist', icon: MessageSquareCode },
    { name: 'Memory Center', path: '/memory', icon: Database },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-charcoal-900 border-r border-charcoal-700 flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-charcoal-700 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-gray-200 to-violet-400 bg-clip-text text-transparent">
              CreatorIQ
            </span>
            <span className="block text-[10px] text-violet-400 font-medium uppercase tracking-wider">
              AI Strategist
            </span>
          </div>
        </div>
      </div>

      {/* Channel Summary Card in Sidebar */}
      {channelData && (
        <div className="mx-4 mt-4 p-3 rounded-xl bg-charcoal-850 border border-charcoal-700/60 flex items-center gap-3">
          {channelData.channel.thumbnail_url ? (
            <img
              src={channelData.channel.thumbnail_url}
              alt={channelData.channel.name}
              className="w-10 h-10 rounded-full object-cover border border-violet-500/30"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-violet-600/20 text-violet-400 flex items-center justify-center font-bold">
              {channelData.channel.name.charAt(0)}
            </div>
          )}
          <div className="overflow-hidden flex-1">
            <h4 className="text-sm font-semibold text-white truncate">{channelData.channel.name}</h4>
            <p className="text-xs text-gray-400 truncate">
              {channelData.channel.subscriber_count !== null && channelData.channel.subscriber_count !== undefined
                ? `${channelData.channel.subscriber_count.toLocaleString()} subs`
                : 'Connected'}
            </p>
          </div>
        </div>
      )}

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
          Analytics & Strategy
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/25'
                    : 'text-gray-400 hover:text-white hover:bg-charcoal-800'
                }`
              }
            >
              <Icon className="w-5 h-5 transition-transform group-hover:scale-110" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer / Disconnect Channel */}
      <div className="p-4 border-t border-charcoal-700">
        <button
          onClick={handleDisconnect}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-red-400 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 transition-all duration-200"
        >
          <LogOut className="w-4 h-4" />
          <span>Switch Channel</span>
        </button>
      </div>
    </aside>
  );
};
