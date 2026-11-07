import axios from 'axios';
import {
  AnalyticsChannelResponse,
  ChannelInsightsResponse,
  ChannelResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const analyzeChannel = async (channelUrl: string): Promise<AnalyticsChannelResponse> => {
  const response = await apiClient.post<AnalyticsChannelResponse>('/api/analytics/channel', {
    channel_url: channelUrl,
  });
  return response.data;
};

export const generateChannelInsights = async (
  channelUrl: string,
): Promise<ChannelInsightsResponse> => {
  const response = await apiClient.post<ChannelInsightsResponse>(
    '/api/insights/channel',
    { channel_url: channelUrl },
    { timeout: 60000 },
  );
  return response.data;
};

export const getYoutubeChannel = async (channelUrl: string): Promise<ChannelResponse> => {
  const response = await apiClient.post<ChannelResponse>('/api/youtube/channel', {
    channel_url: channelUrl,
  });
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string; service: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};
