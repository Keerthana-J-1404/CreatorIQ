"""FastAPI application entry point for CreatorIQ."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analytics import router as analytics_router
from backend.routes.youtube import router as youtube_router

app = FastAPI(title="CreatorIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(youtube_router)
app.include_router(analytics_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return the API's health status."""
    return {"status": "ok", "service": "CreatorIQ API"}
