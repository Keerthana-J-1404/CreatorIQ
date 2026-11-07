import axios from 'axios';
import { AnalyticsChannelResponse, ChannelResponse } from '../types/api';

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

export const getYoutubeChannel = async (channelUrl: string): Promise<ChannelResponse> => {
  const response = await apiClient.post<ChannelResponse>('/api/youtube/channel', {
    channel_url: channelUrl,
  });
  return response.data;
};

export const sendChatMessage = async (channelId: string, message: string, channelContext?: any) => {
  const response = await apiClient.post('/api/chat', {
    channel_id: channelId,
    message,
    channel_context: channelContext,
  });
  return response.data;
};

export const getChannelMemories = async (channelId: string) => {
  const response = await apiClient.get(`/api/memory/${channelId}`);
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string; service: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};
