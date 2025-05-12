from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class JobType(str, Enum):
    VIDEO_PROCESSING = "video_processing"
    VIDEO_DELETION = "video_deletion"
    USER_DELETION = "user_deletion"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobCreate(BaseModel):
    job_type: JobType
    resource_id: str  # ID of the resource being processed (video, user, etc.)
    params: Optional[Dict[str, Any]] = None

class JobInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: JobType
    resource_id: str
    status: JobStatus = JobStatus.QUEUED
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Job(BaseModel):
    id: str
    job_type: JobType
    resource_id: str
    status: JobStatus
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 