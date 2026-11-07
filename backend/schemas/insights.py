from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.analytics import ChannelAnalytics, VideoAnalytics
from backend.schemas.youtube import ChannelInfo, DataSource


class SupportedObservation(BaseModel):
    observation: str = Field(description="A concise, sample-supported observation.")
    supporting_video_titles: list[str] = Field(
        description="Exact titles from the supplied recent-video sample."
    )


class ContentHypothesis(BaseModel):
    hypothesis: str = Field(
        description="A possibility to test, not a finding about the audience."
    )
    rationale: str
    supporting_video_titles: list[str] = Field(
        description="Exact titles from the sample, or an empty list if unsupported."
    )


class ContentPattern(BaseModel):
    category: Literal["topic", "format", "theme"]
    description: str
    supporting_video_titles: list[str]
    performance_observation: str | None = Field(
        description=(
            "A sample-supported comparison with observed performance, or null when "
            "the sample does not support a comparison. Do not claim causation."
        )
    )


class ContentGaps(BaseModel):
    observed_underrepresented: list[SupportedObservation] = Field(
        description="Patterns visibly scarce in the supplied sample, not the full channel."
    )
    hypotheses_to_test: list[ContentHypothesis] = Field(
        description="Clearly labeled possibilities, not claims about audience demand."
    )


class Recommendation(BaseModel):
    recommendation: str
    rationale: str
    supporting_video_titles: list[str] = Field(
        description="Exact titles from the sample, or an empty list if no direct support exists."
    )


class ContentIdea(BaseModel):
    proposed_title: str
    explanation: str
    based_on_video_titles: list[str] = Field(
        description="Exact titles from the sample, or an empty list if none are relevant."
    )


class StrategyDraft(BaseModel):
    assessment: str = Field(
        description="Explain current performance using only supplied sample metrics."
    )
    strongest_observed_patterns: list[SupportedObservation]
    weakest_observed_patterns: list[SupportedObservation]
    content_patterns: list[ContentPattern]
    content_gaps: ContentGaps
    recommendations: list[Recommendation] = Field(
        description="Provide between 3 and 5 actionable recommendations."
    )
    content_ideas: list[ContentIdea] = Field(
        description="Provide exactly 5 ideas."
    )


class ChannelInsightsResponse(StrategyDraft):
    data_source: DataSource
    channel: ChannelInfo
    videos: list[VideoAnalytics]
    analytics: ChannelAnalytics
    sample_scope: str
