import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Database
from .database import get_db, init_db

# Routers
from .routers import photos, analysis, recommendations, progress, profile, skincare, integration, video_learning, event_mode, confidence, experiments, aesthetic_training, posture, nutrition, sleep, stress

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting LookCoach API...")
    init_db()
    print("Database initialized.")
    yield
    # Shutdown
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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LookCoach"}


@app.get("/")
async def root():
    return {"message": "Welcome to LookCoach API", "docs": "/docs"}


# Include routers
app.include_router(photos.router, prefix="/api/photos", tags=["photos"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(skincare.router, prefix="/api/skincare", tags=["skincare"])
app.include_router(integration.router, prefix="/api/integration", tags=["integration"])
app.include_router(video_learning.router, prefix="/api/video-learning", tags=["video-learning"])
app.include_router(event_mode.router, prefix="/api/event-mode", tags=["event-mode"])
app.include_router(confidence.router, prefix="/api/confidence", tags=["confidence"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(aesthetic_training.router, prefix="/api/aesthetic-training", tags=["aesthetic-training"])
app.include_router(posture.router, prefix="/api/posture", tags=["posture"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["nutrition"])
app.include_router(sleep.router, prefix="/api/sleep", tags=["sleep"])
app.include_router(stress.router, prefix="/api/stress", tags=["stress"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
