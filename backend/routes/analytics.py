from fastapi import APIRouter, HTTPException

from backend.schemas.analytics import AnalyticsChannelResponse
from backend.schemas.youtube import ChannelRequest
from backend.services.analytics_service import calculate_channel_analytics
from backend.services.youtube_service import YouTubeServiceError, get_channel_data

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.post("/channel", response_model=AnalyticsChannelResponse)
async def get_channel_analytics(
    request: ChannelRequest,
) -> AnalyticsChannelResponse:
    try:
        channel_data = await get_channel_data(request.channel_url)
        return calculate_channel_analytics(channel_data)
    except YouTubeServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
