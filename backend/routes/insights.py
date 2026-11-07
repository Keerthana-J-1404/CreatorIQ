from fastapi import APIRouter, HTTPException

from backend.schemas.insights import ChannelInsightsResponse
from backend.schemas.youtube import ChannelRequest
from backend.services.insights_service import GeminiServiceError, get_channel_insights
from backend.services.youtube_service import YouTubeServiceError

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.post("/channel", response_model=ChannelInsightsResponse)
async def get_channel_content_strategy(
    request: ChannelRequest,
) -> ChannelInsightsResponse:
    try:
        return await get_channel_insights(request.channel_url)
    except (YouTubeServiceError, GeminiServiceError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
