import React, { useState, useRef, useEffect } from 'react';
import { Header } from '../components/Header';
import { useChannel } from '../context/ChannelContext';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Lightbulb,
  Loader2,
  RefreshCw,
  BrainCircuit
} from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
}

export const AIStrategistPage: React.FC = () => {
  const { channelData } = useChannel();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: `Hello! I am your CreatorIQ AI Strategist. I have analyzed ${channelData?.channel.name || 'your channel'} (${channelData?.analytics.recent_video_count || 0} recent videos loaded, avg views: ${channelData?.analytics.average_views_per_video ? Math.round(channelData.analytics.average_views_per_video).toLocaleString() : 'N/A'}). How can I help you optimize your content strategy today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const suggestedPrompts = [
    "What should I post next?",
    "Why are some of my videos underperforming?",
    "What content does my audience prefer?",
    "Suggest 5 video ideas for my channel.",
    "How can I improve my video hooks?"
  ];

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    if (!textToSend) setInput('');
    setLoading(true);

    // Simulate intelligent AI strategist response leveraging channel analytics
    setTimeout(() => {
      let aiResponseText = "Based on your channel analytics and Hindsight memory profile, ";
      const lower = text.toLowerCase();

      if (lower.includes('next') || lower.includes('post') || lower.includes('ideas')) {
        aiResponseText += `your highest-performing video is "${channelData?.analytics.highest_viewed_video?.title || 'your top video'}" with ${channelData?.analytics.highest_viewed_video?.view_count?.toLocaleString() || 0} views. I recommend creating a follow-up case study or a deeper technical breakdown addressing common questions from that video's comment section.`;
      } else if (lower.includes('underperforming') || lower.includes('why')) {
        aiResponseText += `your recent videos show a variance in views. The ones with lower view counts often suffer from unclear title hooks or lack of immediate problem framing in the opening 15 seconds. Ensure your thumbnail and title create a curiosity loop without over-promising.`;
      } else if (lower.includes('hook') || lower.includes('retention')) {
        aiResponseText += `to improve your video hooks: 1) Skip lengthy channel intros, 2) State the exact viewer benefit or problem in the first 10 seconds, and 3) Show a high-stakes preview of the climax or result early on.`;
      } else if (lower.includes('audience') || lower.includes('prefer')) {
        aiResponseText += `your audience responds best to actionable, high-utility content. Your average engagement rate is ${channelData?.analytics.average_engagement_rate_percent ? channelData.analytics.average_engagement_rate_percent.toFixed(2) + '%' : 'healthy'}, indicating strong loyalty when you solve concrete problems.`;
      } else {
        aiResponseText += `focusing on iterative title optimization and robust hooks will yield the highest return on viewer retention. Your channel average is ${channelData?.analytics.average_views_per_video ? Math.round(channelData.analytics.average_views_per_video).toLocaleString() : 'stable'} views per video. Let's build upon your top outlier formats!`;
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: aiResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages(prev => [...prev, aiMessage]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-charcoal-950 overflow-hidden">
      <Header
        title="AI Content Strategist"
        subtitle="Chat with your channel's personalized AI strategist backed by Hindsight memory"
      />

      <div className="flex-1 flex flex-col max-w-5xl w-full mx-auto p-6 md:p-8 overflow-hidden">
        {/* Chat Container */}
        <div className="flex-1 bg-charcoal-900 border border-charcoal-700/80 rounded-2xl shadow-xl flex flex-col overflow-hidden">
          {/* Chat Header Banner */}
          <div className="px-6 py-4 border-b border-charcoal-700 bg-charcoal-850 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-violet-400">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">CreatorIQ Strategist AI</h3>
                <p className="text-xs text-gray-400">Contextualized for {channelData?.channel.name}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs">
              <BrainCircuit className="w-3.5 h-3.5 animate-pulse" />
              <span>Memory Synchronized</span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start gap-3.5 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                  msg.sender === 'user'
                    ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/30'
                    : 'bg-charcoal-800 text-violet-400 border border-charcoal-700'
                }`}>
                  {msg.sender === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>

                <div className={`max-w-xl rounded-2xl p-4 text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-violet-600 text-white rounded-tr-none shadow-lg shadow-violet-600/20'
                    : 'bg-charcoal-850 text-gray-200 border border-charcoal-700/80 rounded-tl-none'
                }`}>
                  <p>{msg.text}</p>
                  <span className={`block text-[10px] mt-2 ${msg.sender === 'user' ? 'text-violet-200 text-right' : 'text-gray-400'}`}>
                    {msg.timestamp}
                  </span>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-charcoal-800 text-violet-400 border border-charcoal-700 flex items-center justify-center">
                  <Bot className="w-5 h-5" />
                </div>
                <div className="bg-charcoal-850 text-gray-400 border border-charcoal-700/80 rounded-2xl rounded-tl-none p-4 text-sm flex items-center gap-3">
                  <Loader2 className="w-4 h-4 animate-spin text-violet-400" />
                  <span>Synthesizing channel analytics & memory...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Prompts */}
          <div className="px-6 py-3 bg-charcoal-850 border-t border-charcoal-700/60 flex items-center gap-2 overflow-x-auto">
            <span className="text-xs text-gray-400 shrink-0 font-medium flex items-center gap-1">
              <Lightbulb className="w-3.5 h-3.5 text-violet-400" />
              <span>Suggested:</span>
            </span>
            {suggestedPrompts.map((prompt, index) => (
              <button
                key={index}
                onClick={() => handleSend(prompt)}
                disabled={loading}
                className="px-3 py-1.5 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 border border-charcoal-700 text-xs text-gray-300 shrink-0 transition-all disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <div className="p-4 bg-charcoal-900 border-t border-charcoal-700">
            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex items-center gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask your AI strategist anything about your content, hooks, or growth..."
                disabled={loading}
                className="flex-1 bg-charcoal-850 border border-charcoal-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition-all disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-5 py-3 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white font-semibold flex items-center gap-2 shadow-lg shadow-violet-600/30 transition-all shrink-0 cursor-pointer"
              >
                <span>Send</span>
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
