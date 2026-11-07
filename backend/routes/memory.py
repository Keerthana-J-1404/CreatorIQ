from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.hindsight_service import HindsightService

router = APIRouter(prefix="/api", tags=["Hindsight Memory"])


class StoreMemoryRequest(BaseModel):
    channel_id: str
    title: str
    content: str
    category: str


@router.get("/memory/{channel_id}")
async def get_channel_memories(channel_id: str):
    """Retrieve all Hindsight memory clusters for a channel."""
    return HindsightService.get_memory_clusters(channel_id)


@router.post("/memory")
async def store_channel_memory(request: StoreMemoryRequest):
    """Store a new memory node into Hindsight."""
    HindsightService.store_memory(
        channel_id=request.channel_id,
        title=request.title,
        content=request.content,
        category=request.category
    )
    return {"status": "success", "message": "Memory stored successfully in Hindsight."}
