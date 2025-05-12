import logging
import asyncio
from typing import Dict, Any
from celery import Task

from app.core.celery_app import celery_app
from app.services.silence_service import process_video
from app.services.video_service import get_video_by_id
from app.models.video import VideoProcessingSettings

logger = logging.getLogger("silence-cutter")

class AsyncTask(Task):
    """Task that runs an async function in an event loop."""
    
    def run_async(self, coro):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

@celery_app.task(bind=True, base=AsyncTask)
def process_video_task(self, video_id: str) -> Dict[str, Any]:
    """
    Process a video in the background to remove silence
    """
    try:
        # Get video details
        video = self.run_async(get_video_by_id(video_id))
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            return {"status": "error", "error": "Video not found"}
        
        # Process the video
        result = self.run_async(
            process_video(
                video_id=video_id,
                input_file_path=video.original_file_path,
                processing_settings=VideoProcessingSettings(**video.processing_settings.model_dump())
            )
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error in process_video_task: {str(e)}")
        return {
            "status": "error",
            "video_id": video_id,
            "error": str(e)
        }

@celery_app.task(bind=True, base=AsyncTask)
def cleanup_old_videos_task(self) -> Dict[str, Any]:
    """
    Cleanup old temporary videos
    """
    # This would be implemented to clean up old processed videos
    # that are no longer needed, based on some retention policy
    return {"status": "not_implemented"} 