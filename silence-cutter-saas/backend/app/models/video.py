from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SilenceSegment(BaseModel):
    start_time: float  # In seconds
    end_time: float    # In seconds
    duration: float    # In seconds
    
class VideoProcessingSettings(BaseModel):
    silence_threshold_db: float = -40.0
    min_silence_duration_ms: int = 500
    padding_ms: int = 200  # Padding around silence segments
    keep_silence_markers: bool = False  # If True, marks silence instead of removing it
    
class VideoCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    processing_settings: Optional[VideoProcessingSettings] = None

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
class VideoInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: Optional[str] = None
    original_filename: str
    original_file_path: str
    processed_file_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    silence_segments: Optional[List[SilenceSegment]] = None
    processing_settings: VideoProcessingSettings = Field(default_factory=VideoProcessingSettings)
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Video(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    original_filename: str
    duration_seconds: Optional[float] = None
    status: ProcessingStatus
    silence_segments: Optional[List[SilenceSegment]] = None
    processing_settings: VideoProcessingSettings
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VideoWithUrls(Video):
    original_url: Optional[str] = None
    processed_url: Optional[str] = None 