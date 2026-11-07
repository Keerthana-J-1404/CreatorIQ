from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    id: str
    title: str
    content: str
    category: str
    timestamp: str


class MemoryClusterResponse(BaseModel):
    category: str
    items: list[MemoryItem]


class MemoryCenterResponse(BaseModel):
    channel_id: str
    clusters: list[MemoryClusterResponse]
    total_memories: int
    hindsight_status: str
