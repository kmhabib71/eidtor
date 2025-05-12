import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.db.mongodb import get_database
from app.models.job import Job, JobCreate, JobInDB, JobStatus, JobType

logger = logging.getLogger("silence-cutter")

async def get_job_collection():
    db = await get_database()
    return db.jobs

async def create_job(job_create: JobCreate) -> Job:
    """
    Create a new job
    """
    jobs = await get_job_collection()
    
    # Create job in DB
    job_in_db = JobInDB(
        job_type=job_create.job_type,
        resource_id=job_create.resource_id,
        params=job_create.params
    )
    
    # Insert into database
    await jobs.insert_one(job_in_db.model_dump())
    
    # Return job
    return await get_job_by_id(job_in_db.id)

async def get_job_by_id(job_id: str) -> Optional[Job]:
    """
    Get a job by ID
    """
    jobs = await get_job_collection()
    job_data = await jobs.find_one({"id": job_id})
    
    if not job_data:
        return None
    
    return Job(**job_data)

async def get_jobs_by_resource_id(resource_id: str) -> List[Job]:
    """
    Get all jobs for a resource
    """
    jobs = await get_job_collection()
    job_list = []
    
    cursor = jobs.find({"resource_id": resource_id}).sort("created_at", -1)
    async for job_data in cursor:
        job = Job(**job_data)
        job_list.append(job)
    
    return job_list

async def get_jobs_by_status(status: JobStatus, limit: int = 100) -> List[Job]:
    """
    Get jobs by status
    """
    jobs = await get_job_collection()
    job_list = []
    
    cursor = jobs.find({"status": status}).sort("created_at", -1).limit(limit)
    async for job_data in cursor:
        job = Job(**job_data)
        job_list.append(job)
    
    return job_list

async def update_job_status(
    job_id: str,
    status: JobStatus,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Optional[Job]:
    """
    Update job status
    """
    jobs = await get_job_collection()
    
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    if status == JobStatus.RUNNING and "started_at" not in update_data:
        update_data["started_at"] = datetime.utcnow()
    
    if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        update_data["completed_at"] = datetime.utcnow()
    
    if result is not None:
        update_data["result"] = result
    
    if error is not None:
        update_data["error"] = error
    
    await jobs.update_one(
        {"id": job_id},
        {"$set": update_data}
    )
    
    return await get_job_by_id(job_id)

async def delete_job(job_id: str) -> bool:
    """
    Delete a job
    """
    jobs = await get_job_collection()
    result = await jobs.delete_one({"id": job_id})
    return result.deleted_count > 0

async def cleanup_old_jobs(days: int = 30) -> int:
    """
    Delete jobs older than specified days
    """
    jobs = await get_job_collection()
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await jobs.delete_many({
        "created_at": {"$lt": cutoff_date},
        "status": {"$in": [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]}
    })
    
    return result.deleted_count 