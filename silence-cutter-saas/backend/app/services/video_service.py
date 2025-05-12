import logging
import os
import shutil
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException
import aiofiles
from moviepy.editor import VideoFileClip
import mimetypes

from app.core.config import settings
from app.db.mongodb import get_database
from app.models.user import User
from app.models.video import Video, VideoCreate, VideoInDB, VideoUpdate, ProcessingStatus, VideoWithUrls
from app.services.storage_service import save_file_to_storage, get_file_url

logger = logging.getLogger("silence-cutter")

async def get_video_collection():
    db = await get_database()
    return db.videos

async def create_video(
    user: User, 
    file: UploadFile, 
    video_data: VideoCreate
) -> Video:
    """
    Create a new video entry and save the uploaded file
    """
    # Create directories if they don't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate a unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save the file
    try:
        # Write file to disk
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Get video metadata
        duration = None
        try:
            with VideoFileClip(file_path) as clip:
                duration = clip.duration
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
        
        # Save file to permanent storage (S3, GCS, etc.)
        storage_path = await save_file_to_storage(
            file_path=file_path,
            destination_path=f"uploads/{user.id}/{unique_filename}"
        )
        
        # Create video object
        title = video_data.title or os.path.splitext(file.filename)[0]
        
        video_in_db = VideoInDB(
            user_id=user.id,
            title=title,
            description=video_data.description,
            original_filename=file.filename,
            original_file_path=storage_path,
            duration_seconds=duration,
            size_bytes=file_size,
            mime_type=mime_type,
            processing_settings=video_data.processing_settings or None
        )
        
        # Save to database
        videos = await get_video_collection()
        await videos.insert_one(video_in_db.model_dump())
        
        # Return video info
        return await get_video_by_id(video_in_db.id)
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

async def get_video_by_id(video_id: str) -> Optional[VideoWithUrls]:
    """Get a video by ID with URLs"""
    videos = await get_video_collection()
    video_data = await videos.find_one({"id": video_id})
    
    if not video_data:
        return None
    
    video = Video(**video_data)
    
    # Add URLs
    video_with_urls = VideoWithUrls(
        **video.model_dump(),
        original_url=await get_file_url(video.original_file_path) if video.original_file_path else None,
        processed_url=await get_file_url(video.processed_file_path) if video.processed_file_path else None
    )
    
    return video_with_urls

async def get_videos_by_user(user_id: str, skip: int = 0, limit: int = 100) -> List[VideoWithUrls]:
    """Get all videos for a user"""
    videos = await get_video_collection()
    video_list = []
    
    cursor = videos.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    async for video_data in cursor:
        video = Video(**video_data)
        video_with_urls = VideoWithUrls(
            **video.model_dump(),
            original_url=await get_file_url(video.original_file_path) if video.original_file_path else None,
            processed_url=await get_file_url(video.processed_file_path) if video.processed_file_path else None
        )
        video_list.append(video_with_urls)
    
    return video_list

async def update_video(video_id: str, update_data: VideoUpdate) -> Optional[VideoWithUrls]:
    """Update video details"""
    videos = await get_video_collection()
    video = await get_video_by_id(video_id)
    
    if not video:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    await videos.update_one(
        {"id": video_id},
        {"$set": update_dict}
    )
    
    return await get_video_by_id(video_id)

async def delete_video(video_id: str) -> bool:
    """Delete a video and its files"""
    videos = await get_video_collection()
    video = await get_video_by_id(video_id)
    
    if not video:
        return False
    
    # Delete from storage service would go here
    # For now, just delete from database
    
    result = await videos.delete_one({"id": video_id})
    return result.deleted_count > 0

async def update_video_status(
    video_id: str, 
    status: ProcessingStatus, 
    error_message: Optional[str] = None,
    processed_file_path: Optional[str] = None,
    processing_time_seconds: Optional[float] = None,
    silence_segments: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Video]:
    """Update video processing status"""
    videos = await get_video_collection()
    
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    if error_message is not None:
        update_data["error_message"] = error_message
    
    if processed_file_path is not None:
        update_data["processed_file_path"] = processed_file_path
    
    if processing_time_seconds is not None:
        update_data["processing_time_seconds"] = processing_time_seconds
    
    if silence_segments is not None:
        update_data["silence_segments"] = silence_segments
    
    await videos.update_one(
        {"id": video_id},
        {"$set": update_data}
    )
    
    return await get_video_by_id(video_id) 