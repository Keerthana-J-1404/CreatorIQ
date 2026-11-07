from fastapi import APIRouter, HTTPException

from backend.schemas.analytics import AnalyticsChannelResponse
from backend.schemas.youtube import ChannelRequest
from backend.services.analytics_snapshot_service import get_analytics_snapshot
from backend.services.youtube_service import YouTubeServiceError

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.post("/channel", response_model=AnalyticsChannelResponse)
async def get_channel_analytics(
    request: ChannelRequest,
) -> AnalyticsChannelResponse:
    try:
        return await get_analytics_snapshot(request.channel_url)
    except YouTubeServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
