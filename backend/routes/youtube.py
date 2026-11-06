from fastapi import APIRouter, HTTPException

from backend.schemas.youtube import ChannelRequest, ChannelResponse
from backend.services.youtube_service import YouTubeServiceError, get_channel_data

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])


@router.post("/channel", response_model=ChannelResponse)
async def get_youtube_channel(request: ChannelRequest) -> ChannelResponse:
    try:
        return await get_channel_data(request.channel_url)
    except YouTubeServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
