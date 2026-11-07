import React from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useChannel } from '../context/ChannelContext';

export const Layout: React.FC = () => {
  const { channelData } = useChannel();
  const location = useLocation();

  // If trying to access protected pages without channel data, redirect to landing
  if (!channelData && location.pathname !== '/') {
    return <Navigate to="/" replace />;
  }

  // If on landing page and channel data exists, user can still view landing or go to dashboard
  return (
    <div className="flex min-h-screen bg-charcoal-950 text-gray-100">
      {channelData && <Sidebar />}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};
