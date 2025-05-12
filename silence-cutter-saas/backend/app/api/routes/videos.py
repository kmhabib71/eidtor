import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from pydantic import parse_obj_as

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.video import Video, VideoCreate, VideoUpdate, VideoWithUrls, VideoProcessingSettings
from app.services.video_service import (
    create_video,
    get_video_by_id,
    get_videos_by_user,
    update_video,
    delete_video
)
from app.tasks.video_tasks import process_video_task

logger = logging.getLogger("silence-cutter")

router = APIRouter()

@router.post("/upload", response_model=VideoWithUrls, status_code=status.HTTP_201_CREATED)
async def upload_video(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    silence_threshold_db: float = Form(-40.0),
    min_silence_duration_ms: int = Form(500),
    padding_ms: int = Form(200),
    keep_silence_markers: bool = Form(False),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new video
    """
    # Check if user has reached their limit
    if current_user.processing_minutes_used >= current_user.processing_minutes_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have reached your monthly processing limit"
        )
    
    # Check file size (if configured)
    if hasattr(file, "size") and file.size > (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed ({settings.MAX_UPLOAD_SIZE_MB}MB)"
        )
    
    # Create video processing settings
    processing_settings = VideoProcessingSettings(
        silence_threshold_db=silence_threshold_db,
        min_silence_duration_ms=min_silence_duration_ms,
        padding_ms=padding_ms,
        keep_silence_markers=keep_silence_markers
    )
    
    # Create video data object
    video_data = VideoCreate(
        title=title,
        description=description,
        processing_settings=processing_settings
    )
    
    # Create video entry and save file
    video = await create_video(current_user, file, video_data)
    
    # Start processing in background
    process_video_task.delay(video.id)
    
    return video

@router.get("/", response_model=List[VideoWithUrls])
async def get_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all videos for the current user
    """
    videos = await get_videos_by_user(current_user.id, skip=skip, limit=limit)
    return videos

@router.get("/{video_id}", response_model=VideoWithUrls)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific video by ID
    """
    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if user has access to this video
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this video"
        )
    
    return video

@router.patch("/{video_id}", response_model=VideoWithUrls)
async def update_video_metadata(
    video_id: str,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update video metadata
    """
    # Get the video
    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if user has access to this video
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this video"
        )
    
    # Update the video
    updated_video = await update_video(video_id, video_update)
    return updated_video

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video_by_id(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a video
    """
    # Get the video
    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if user has access to this video
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video"
        )
    
    # Delete the video
    success = await delete_video(video_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video"
        )
    
    return None

@router.post("/{video_id}/process", response_model=dict)
async def process_video_endpoint(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Process a video to remove silence
    """
    # Get the video
    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if user has access to this video
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process this video"
        )
    
    # Check if video is already being processed
    if video.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is already being processed"
        )
    
    # Start processing task
    task = process_video_task.delay(video_id)
    
    return {
        "message": "Video processing started",
        "task_id": task.id,
        "video_id": video_id
    } 