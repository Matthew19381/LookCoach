import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Routers
from .routers import (
    photos,
    analysis,
    recommendations,
    progress,
    profile,
    skincare,
    integration,
    video_learning,
    event_mode,
    confidence,
    experiments,
    aesthetic_training,
    posture,
    nutrition,
    sleep,
    stress,
    summary,
    consistency,
    directives,
    feedback_loop,
    data,
    ecosystem,
    style,
)

# Database
from .database import init_db
from .paths import UPLOAD_DIR
from .services import outbox

# Environment variables - load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")



OUTBOX_INTERVAL_S = int(os.getenv("LOOKCOACH_OUTBOX_INTERVAL", "60"))


async def _outbox_worker() -> None:
    """Plan 3.1: retry queued hub events (hub restarted, network back, key fixed)."""
    while True:
        await asyncio.sleep(OUTBOX_INTERVAL_S)
        await outbox.deliver_in_new_session()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting LookCoach API...")
    init_db()
    print("Database initialized.")
    worker = asyncio.create_task(_outbox_worker()) if OUTBOX_INTERVAL_S > 0 else None
    yield
    # Shutdown
    if worker:
        worker.cancel()
    print("Shutting down LookCoach API...")


app = FastAPI(
    title="LookCoach API",
    description="AI-powered Looks Optimizer",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LookCoach"}


@app.get("/")
async def root():
    return {"message": "Welcome to LookCoach API", "docs": "/docs"}


# Include routers
app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(skincare.router, prefix="/api/v1/skincare", tags=["skincare"])
app.include_router(integration.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(summary.router, prefix="/api/v1", tags=["summary"])
app.include_router(video_learning.router, prefix="/api/v1/video-learning", tags=["video-learning"])
app.include_router(event_mode.router, prefix="/api/v1/event-mode", tags=["event-mode"])
app.include_router(confidence.router, prefix="/api/v1/confidence", tags=["confidence"])
app.include_router(experiments.router, prefix="/api/v1/experiments", tags=["experiments"])
app.include_router(aesthetic_training.router, prefix="/api/v1/aesthetic-training", tags=["aesthetic-training"])
app.include_router(posture.router, prefix="/api/v1/posture", tags=["posture"])
app.include_router(nutrition.router, prefix="/api/v1/nutrition", tags=["nutrition"])
app.include_router(sleep.router, prefix="/api/v1/sleep", tags=["sleep"])
app.include_router(stress.router, prefix="/api/v1/stress", tags=["stress"])
app.include_router(consistency.router, prefix="/api/v1/consistency", tags=["consistency"])
app.include_router(directives.router, prefix="/api/v1/directives", tags=["directives"])
app.include_router(feedback_loop.router, prefix="/api/v1/feedback-loop", tags=["feedback-loop"])
app.include_router(data.router, prefix="/api/v1/data", tags=["privacy"])
app.include_router(ecosystem.router, prefix="/api/v1/ecosystem", tags=["ecosystem"])
app.include_router(style.router, prefix="/api/v1/style", tags=["style"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
