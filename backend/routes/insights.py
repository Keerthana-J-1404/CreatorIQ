from fastapi import APIRouter, HTTPException

from backend.schemas.insights import ChannelInsightsResponse
from backend.schemas.youtube import ChannelRequest
from backend.services.analytics_snapshot_service import get_analytics_snapshot
from backend.services.insights_service import GeminiServiceError, get_channel_insights
from backend.services.youtube_service import YouTubeServiceError

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.post("/channel", response_model=ChannelInsightsResponse)
async def get_channel_content_strategy(
    request: ChannelRequest,
) -> ChannelInsightsResponse:
    try:
        analytics_snapshot = await get_analytics_snapshot(request.channel_url)
        return await get_channel_insights(analytics_snapshot)
    except (YouTubeServiceError, GeminiServiceError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
