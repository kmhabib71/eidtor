from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
import uuid
import logging
from datetime import datetime

from app.core.config import settings
from app.api.routes import auth, videos, users, admin, jobs
from app.core.logging import setup_logging
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.core.dependencies import get_current_user

# Setup logging
setup_logging()
logger = logging.getLogger("silence-cutter")

app = FastAPI(
    title="Silence Cutter API",
    description="API for removing silence from videos",
    version="1.0.0",
)

# Set up CORS middleware
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "https://silence-cutter.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB on startup
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    logger.info("Connected to MongoDB")

# Close MongoDB connection on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    logger.info("Disconnected from MongoDB")

# Include all API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

# Mount static files directory for temporary files
os.makedirs(settings.STATIC_FILES_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.STATIC_FILES_DIR), name="static")

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Silence Cutter API. Go to /docs for documentation."}

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 