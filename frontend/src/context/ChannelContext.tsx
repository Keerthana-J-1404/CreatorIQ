import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AnalyticsChannelResponse } from '../types/api';
import { analyzeChannel } from '../services/api';

interface ChannelContextType {
  channelData: AnalyticsChannelResponse | null;
  loading: boolean;
  error: string | null;
  currentChannelUrl: string;
  analyze: (url: string) => Promise<void>;
  clearChannel: () => void;
}

const ChannelContext = createContext<ChannelContextType | undefined>(undefined);

const STORAGE_KEY = 'creatoriq_channel_data';
const URL_STORAGE_KEY = 'creatoriq_channel_url';

export const ChannelProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [channelData, setChannelData] = useState<AnalyticsChannelResponse | null>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [currentChannelUrl, setCurrentChannelUrl] = useState<string>(() => {
    return localStorage.getItem(URL_STORAGE_KEY) || '';
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (channelData) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(channelData));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [channelData]);

  useEffect(() => {
    if (currentChannelUrl) {
      localStorage.setItem(URL_STORAGE_KEY, currentChannelUrl);
    } else {
      localStorage.removeItem(URL_STORAGE_KEY);
    }
  }, [currentChannelUrl]);

  const analyze = async (url: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeChannel(url);
      setChannelData(data);
      setCurrentChannelUrl(url);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to analyze channel. Please check the URL and try again.';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const clearChannel = () => {
    setChannelData(null);
    setCurrentChannelUrl('');
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(URL_STORAGE_KEY);
  };

  return (
    <ChannelContext.Provider
      value={{
        channelData,
        loading,
        error,
        currentChannelUrl,
        analyze,
        clearChannel,
      }}
    >
      {children}
    </ChannelContext.Provider>
  );
};

export const useChannel = () => {
  const context = useContext(ChannelContext);
  if (!context) {
    throw new Error('useChannel must be used within a ChannelProvider');
  }
  return context;
};
