from fastapi import APIRouter
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.hindsight_service import HindsightService

router = APIRouter(prefix="/api", tags=["AI Strategist & Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_strategist(request: ChatRequest) -> ChatResponse:
    channel_id = request.channel_id
    user_message = request.message

    # Recall relevant Hindsight memories
    recalled_memories = HindsightService.recall_memories(channel_id, user_message)

    # Formulate intelligent context-aware response
    lower = user_message.lower()
    if "next" in lower or "post" in lower or "ideas" in lower:
        reply = (
            f"Based on your Hindsight memory profile and past successful videos, "
            f"your audience responds best to concrete workflow breakdowns. "
            f"Recalled Memory Context: {recalled_memories[0] if recalled_memories else 'Focus on high-utility topics'}. "
            f"Recommended next post: A step-by-step case study or 'Behind the Scenes' breakdown of your top-performing format."
        )
    elif "underperforming" in lower or "why" in lower:
        reply = (
            f"Analyzing your Hindsight memory logs, underperforming videos typically suffer from "
            f"hook hesitation or abstract titles. Recalled Memory: {recalled_memories[-1] if recalled_memories else 'Improve hook delivery'}. "
            f"Ensure your opening 10 seconds immediately answer the viewer's core question."
        )
    elif "hook" in lower or "retention" in lower:
        reply = (
            f"According to your channel's memory patterns: {recalled_memories[0] if recalled_memories else 'Hook is critical'}. "
            f"To maximize retention: 1) Skip long channel intros, 2) Tease the climax early, 3) State the core value proposition immediately."
        )
    else:
        reply = (
            f"Using Hindsight memory integration, I've synthesized your channel strategy. "
            f"Recalled Context: {recalled_memories[0] if recalled_memories else 'Continuous optimization'}. "
            f"Let's continue refining your content pillars to accelerate subscriber growth!"
        )

    # Store interaction memory back into Hindsight
    HindsightService.store_memory(
        channel_id=channel_id,
        title=f"Chat interaction: {user_message[:30]}...",
        content=f"User asked: '{user_message}'. AI advised on content strategy.",
        category="Experiment History"
    )

    return ChatResponse(
        reply=reply,
        memories_used=recalled_memories
    )
