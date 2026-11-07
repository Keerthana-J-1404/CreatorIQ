import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import {
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  Lightbulb,
  Loader2,
  RefreshCw,
  Sparkles,
  Target,
  TrendingDown,
  TrendingUp,
  Video,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Header } from '../components/Header';
import { useChannel } from '../context/ChannelContext';
import { generateChannelInsights } from '../services/api';
import {
  ChannelInsightsResponse,
  VideoAnalytics,
} from '../types/api';

const formatNumber = (value: number | null | undefined): string =>
  value === null || value === undefined ? 'Not available' : Math.round(value).toLocaleString();

const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const detail: unknown = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (detail !== undefined && detail !== null) {
      return JSON.stringify(detail);
    }
    if (error.message) {
      return error.message;
    }
  }
  return 'The strategy could not be generated. Please try again.';
};

const EvidenceLinks: React.FC<{
  titles: string[];
  videos: VideoAnalytics[];
}> = ({ titles, videos }) => {
  if (titles.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t border-charcoal-700/70 pt-3">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-gray-500">
        Sample video evidence
      </p>
      <ul className="flex flex-wrap gap-2">
        {titles.map((title, index) => {
          const video = videos.find((candidate) => candidate.title === title);
          return (
            <li key={`${title}-${index}`}>
              {video ? (
                <a
                  href={video.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex max-w-full items-center gap-1 rounded-lg border border-charcoal-700 bg-charcoal-950/70 px-2.5 py-1.5 text-xs text-violet-300 hover:border-violet-500/50 hover:text-violet-200"
                >
                  <span className="truncate">{title}</span>
                  <ArrowUpRight className="h-3 w-3 shrink-0" />
                </a>
              ) : (
                <span className="inline-flex max-w-full rounded-lg border border-charcoal-700 bg-charcoal-950/70 px-2.5 py-1.5 text-xs text-gray-400">
                  {title}
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};

const ReportSection: React.FC<{
  title: string;
  description?: string;
  icon: React.ElementType;
  children: React.ReactNode;
}> = ({ title, description, icon: Icon, children }) => (
  <section className="rounded-2xl border border-charcoal-700/80 bg-charcoal-900 p-5 shadow-lg md:p-6">
    <div className="mb-5 flex items-start gap-3">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-violet-500/20 bg-violet-600/10 text-violet-300">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <h2 className="text-base font-bold text-white">{title}</h2>
        {description && <p className="mt-1 text-sm text-gray-400">{description}</p>}
      </div>
    </div>
    {children}
  </section>
);

const EmptySection: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <p className="rounded-xl border border-dashed border-charcoal-700 px-4 py-3 text-sm text-gray-400">
    {children}
  </p>
);

const PatternCards: React.FC<{
  observations: ChannelInsightsResponse['strongest_observed_patterns'];
  videos: VideoAnalytics[];
}> = ({ observations, videos }) => (
  observations.length ? (
    <div className="grid gap-3">
      {observations.map((item, index) => (
        <article key={`${item.observation}-${index}`} className="rounded-xl bg-charcoal-850 p-4">
          <p className="text-sm leading-relaxed text-gray-200">{item.observation}</p>
          <EvidenceLinks titles={item.supporting_video_titles} videos={videos} />
        </article>
      ))}
    </div>
  ) : (
    <EmptySection>No supported observations were returned for this section.</EmptySection>
  )
);

const StrategyReport: React.FC<{ report: ChannelInsightsResponse }> = ({ report }) => {
  const isDemo = report.data_source === 'demo';
  const { analytics } = report;
  const metrics = [
    {
      label: 'Average views per video',
      value: formatNumber(analytics.average_views_per_video),
      icon: TrendingUp,
    },
    {
      label: 'Average engagement rate',
      value: analytics.average_engagement_rate_percent == null
        ? 'Not available'
        : `${analytics.average_engagement_rate_percent.toFixed(2)}%`,
      icon: BarChart3,
    },
    {
      label: 'Recent video views',
      value: formatNumber(analytics.total_recent_video_views),
      icon: Video,
    },
    {
      label: 'Videos in sample',
      value: analytics.recent_video_count.toLocaleString(),
      icon: Target,
    },
  ];

  return (
    <div className="space-y-6">
      <div
        role="status"
        className={`flex items-start gap-3 rounded-xl border px-4 py-3 text-sm ${
          isDemo
            ? 'border-amber-500/30 bg-amber-500/10 text-amber-100'
            : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
        }`}
      >
        {isDemo
          ? <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />}
        <p>
          <strong>{isDemo ? 'Demo analytics:' : 'YouTube API data:'}</strong>{' '}
          {isDemo
            ? 'This strategy is based on synthetic, illustrative analytics and does not describe actual channel performance.'
            : 'This strategy uses retrieved YouTube channel and recent-video data.'}
        </p>
      </div>

      <section className="relative overflow-hidden rounded-2xl border border-violet-500/20 bg-gradient-to-br from-violet-600/15 via-charcoal-900 to-charcoal-900 p-6 shadow-xl md:p-8">
        <div className="relative flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div className="max-w-3xl">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-violet-300">
              AI channel strategy
            </p>
            <h2 className="text-2xl font-extrabold tracking-tight text-white md:text-3xl">
              {report.channel.name}
            </h2>
            <p className="mt-4 text-sm leading-7 text-gray-200 md:text-base">
              {report.assessment}
            </p>
          </div>
        </div>
      </section>

      <section aria-label="Recent video sample metrics">
        <div className="mb-3 flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-violet-300" />
          <h2 className="text-sm font-bold text-white">Recent-video sample metrics</h2>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map(({ label, value, icon: Icon }) => (
            <div key={label} className="rounded-xl border border-charcoal-700/80 bg-charcoal-900 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs text-gray-400">{label}</p>
                <Icon className="h-4 w-4 shrink-0 text-violet-300" />
              </div>
              <p className="mt-3 text-xl font-bold text-white">{value}</p>
            </div>
          ))}
        </div>
        <p className="mt-2 text-xs text-gray-500">
          These values describe only the retrieved recent-video sample, not lifetime channel performance.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <ReportSection
          title="Strongest observed patterns"
          description="Patterns supported by the returned recent-video sample."
          icon={TrendingUp}
        >
          <PatternCards
            observations={report.strongest_observed_patterns}
            videos={report.videos}
          />
        </ReportSection>

        <ReportSection
          title="Weakest observed patterns"
          description="Sample-supported weaker results; these do not establish cause."
          icon={TrendingDown}
        >
          <PatternCards
            observations={report.weakest_observed_patterns}
            videos={report.videos}
          />
        </ReportSection>
      </div>

      <ReportSection
        title="Content patterns"
        description="Topics, formats, and themes identified in the sample."
        icon={Sparkles}
      >
        {report.content_patterns.length ? (
          <div className="grid gap-3 md:grid-cols-2">
            {report.content_patterns.map((pattern, index) => (
              <article
                key={`${pattern.category}-${pattern.description}-${index}`}
                className="rounded-xl bg-charcoal-850 p-4"
              >
                <span className="rounded-md border border-violet-500/20 bg-violet-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-violet-300">
                  {pattern.category}
                </span>
                <p className="mt-3 text-sm leading-relaxed text-gray-200">{pattern.description}</p>
                {pattern.performance_observation && (
                  <p className="mt-2 text-sm leading-relaxed text-gray-400">
                    {pattern.performance_observation}
                  </p>
                )}
                <EvidenceLinks titles={pattern.supporting_video_titles} videos={report.videos} />
              </article>
            ))}
          </div>
        ) : (
          <EmptySection>No content patterns were returned.</EmptySection>
        )}
      </ReportSection>

      <ReportSection
        title="Content gaps"
        description="Observed sample gaps are separated from possibilities that still need testing."
        icon={Target}
      >
        <div className="grid gap-5 lg:grid-cols-2">
          <div>
            <h3 className="mb-3 text-sm font-semibold text-white">Observed underrepresented areas</h3>
            {report.content_gaps.observed_underrepresented.length ? (
              <div className="space-y-3">
                {report.content_gaps.observed_underrepresented.map((item, index) => (
                  <article key={`${item.observation}-${index}`} className="rounded-xl bg-charcoal-850 p-4">
                    <p className="text-sm leading-relaxed text-gray-200">{item.observation}</p>
                    <EvidenceLinks titles={item.supporting_video_titles} videos={report.videos} />
                  </article>
                ))}
              </div>
            ) : (
              <EmptySection>No observed underrepresented areas were returned.</EmptySection>
            )}
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-white">Hypotheses to test</h3>
            {report.content_gaps.hypotheses_to_test.length ? (
              <div className="space-y-3">
                {report.content_gaps.hypotheses_to_test.map((item, index) => (
                  <article key={`${item.hypothesis}-${index}`} className="rounded-xl bg-charcoal-850 p-4">
                    <span className="mb-2 inline-flex items-center gap-1 rounded-md border border-amber-500/20 bg-amber-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-amber-200">
                      <Lightbulb className="h-3 w-3" />
                      Hypothesis to test
                    </span>
                    <p className="mt-1 text-sm font-semibold text-gray-100">{item.hypothesis}</p>
                    <p className="mt-2 text-sm leading-relaxed text-gray-400">{item.rationale}</p>
                    <EvidenceLinks titles={item.supporting_video_titles} videos={report.videos} />
                  </article>
                ))}
              </div>
            ) : (
              <EmptySection>No hypotheses to test were returned.</EmptySection>
            )}
          </div>
        </div>
      </ReportSection>

      <ReportSection
        title="Recommendations"
        description="Actionable next steps grounded in this report's sample and analysis."
        icon={CheckCircle2}
      >
        {report.recommendations.length ? (
          <ol className="grid gap-3 md:grid-cols-2">
            {report.recommendations.map((item, index) => (
              <li key={`${item.recommendation}-${index}`} className="rounded-xl bg-charcoal-850 p-4">
                <div className="mb-3 flex h-7 w-7 items-center justify-center rounded-lg bg-violet-600/20 text-xs font-bold text-violet-200">
                  {index + 1}
                </div>
                <h3 className="text-sm font-semibold leading-relaxed text-white">
                  {item.recommendation}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-400">{item.rationale}</p>
                <EvidenceLinks titles={item.supporting_video_titles} videos={report.videos} />
              </li>
            ))}
          </ol>
        ) : (
          <EmptySection>No recommendations were returned.</EmptySection>
        )}
      </ReportSection>

      <ReportSection
        title="Five content ideas"
        description="Ideas returned by the strategy service; supporting sample videos are linked where available."
        icon={Lightbulb}
      >
        {report.content_ideas.length ? (
          <div className="grid gap-3 md:grid-cols-2">
            {report.content_ideas.map((idea, index) => (
              <article key={`${idea.proposed_title}-${index}`} className="rounded-xl bg-charcoal-850 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-violet-300">
                  Idea {index + 1}
                </p>
                <h3 className="mt-2 text-base font-bold text-white">{idea.proposed_title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-400">{idea.explanation}</p>
                <EvidenceLinks titles={idea.based_on_video_titles} videos={report.videos} />
              </article>
            ))}
          </div>
        ) : (
          <EmptySection>No content ideas were returned.</EmptySection>
        )}
      </ReportSection>

      <ReportSection
        title="Analysis scope"
        description="What this report can and cannot represent."
        icon={Video}
      >
        <p className="text-sm leading-7 text-gray-300">{report.sample_scope}</p>
        <p className="mt-3 text-xs leading-5 text-gray-500">
          Available analytics describe retrieved recent videos only. Missing metrics are shown as unavailable, not as zero.
        </p>
      </ReportSection>
    </div>
  );
};

export const AIStrategistPage: React.FC = () => {
  const { currentChannelUrl, channelData } = useChannel();
  const [report, setReport] = useState<ChannelInsightsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const requestInProgress = useRef(false);
  const requestId = useRef(0);

  useEffect(() => {
    requestId.current += 1;
    requestInProgress.current = false;
    setReport(null);
    setError(null);
    setLoading(false);
  }, [currentChannelUrl, channelData?.channel.channel_id]);

  const handleGenerate = async () => {
    if (!currentChannelUrl || requestInProgress.current) {
      return;
    }

    requestInProgress.current = true;
    const activeRequestId = ++requestId.current;
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const result = await generateChannelInsights(currentChannelUrl);
      if (requestId.current === activeRequestId) {
        setReport(result);
      }
    } catch (requestError: unknown) {
      if (requestId.current === activeRequestId) {
        setError(getErrorMessage(requestError));
      }
    } finally {
      if (requestId.current === activeRequestId) {
        requestInProgress.current = false;
        setLoading(false);
      }
    }
  };

  return (
    <div className="flex min-h-screen flex-1 flex-col bg-charcoal-950">
      <Header
        title="AI Content Strategist"
        subtitle="Generate a structured strategy from your channel's retrieved analytics"
      />

      <main className="mx-auto w-full max-w-7xl flex-1 space-y-6 p-4 sm:p-6 lg:p-8">
        {!currentChannelUrl || !channelData ? (
          <section className="mx-auto mt-8 max-w-2xl rounded-2xl border border-charcoal-700/80 bg-charcoal-900 p-6 text-center shadow-xl sm:mt-16 sm:p-10">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-violet-500/20 bg-violet-600/10 text-violet-300">
              <BarChart3 className="h-6 w-6" />
            </div>
            <h2 className="mt-5 text-xl font-bold text-white">Analyze a channel first</h2>
            <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-gray-400">
              The strategy report needs a selected channel and its analytics. Return to the dashboard to analyze a YouTube channel.
            </p>
            <Link
              to="/dashboard"
              className="mt-6 inline-flex items-center justify-center rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-violet-700"
            >
              Go to dashboard
            </Link>
          </section>
        ) : (
          <>
            <section className="flex flex-col gap-4 rounded-2xl border border-charcoal-700/80 bg-charcoal-900 p-5 shadow-lg sm:flex-row sm:items-center sm:justify-between sm:p-6">
              <div className="max-w-2xl">
                <div className="flex items-center gap-2 text-violet-300">
                  <Sparkles className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-[0.14em]">
                    Strategy report
                  </span>
                </div>
                <h2 className="mt-2 text-xl font-bold text-white">
                  {report ? `Strategy for ${report.channel.name}` : `Build a strategy for ${channelData.channel.name}`}
                </h2>
                <p className="mt-1 text-sm leading-6 text-gray-400">
                  Review observed patterns, sample content gaps, actionable recommendations, and five content ideas.
                </p>
              </div>
              <button
                type="button"
                onClick={handleGenerate}
                disabled={loading}
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-950/30 transition-colors hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating strategy…
                  </>
                ) : report ? (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    Regenerate strategy
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Generate strategy
                  </>
                )}
              </button>
            </section>

            {loading && (
              <div
                role="status"
                aria-live="polite"
                className="flex items-center gap-3 rounded-xl border border-violet-500/20 bg-violet-600/10 px-4 py-4 text-sm text-violet-100"
              >
                <Loader2 className="h-5 w-5 animate-spin text-violet-300" />
                Generating a strategy from the selected channel’s analytics. This may take up to a minute.
              </div>
            )}

            {error && (
              <div
                role="alert"
                className="flex flex-col gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-4 text-sm text-red-100 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="flex items-start gap-2">
                  <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                  <p>{error}</p>
                </div>
                <button
                  type="button"
                  onClick={handleGenerate}
                  disabled={loading}
                  className="shrink-0 rounded-lg border border-red-400/30 px-3 py-2 text-xs font-semibold text-red-100 hover:bg-red-500/10 disabled:opacity-60"
                >
                  Retry
                </button>
              </div>
            )}

            {report && <StrategyReport report={report} />}

            {!report && !loading && !error && (
              <section className="rounded-2xl border border-dashed border-charcoal-700 bg-charcoal-900/60 p-6 text-center sm:p-10">
                <Sparkles className="mx-auto h-7 w-7 text-violet-300" />
                <h3 className="mt-3 text-base font-semibold text-white">
                  Your structured strategy report is ready to generate
                </h3>
                <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-gray-400">
                  The report uses the backend’s channel-specific analytics and recent video sample. It separates observed patterns from hypotheses and labels the data source.
                </p>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
};
