from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    channel_id: str = Field(description="YouTube channel ID or handle")
    message: str = Field(description="User prompt/message for the AI strategist")
    channel_context: dict | None = Field(default=None, description="Optional channel analytics context")


class ChatResponse(BaseModel):
    reply: str = Field(description="AI strategist response")
    memories_used: list[str] = Field(description="Hindsight memories recalled and utilized")
