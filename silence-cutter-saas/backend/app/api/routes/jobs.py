import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from celery.result import AsyncResult

from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.core.celery_app import celery_app

logger = logging.getLogger("silence-cutter")

router = APIRouter()

@router.get("/tasks/{task_id}", response_model=dict)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the status of a background task
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    # Add result or error info if task is finished
    if task_result.ready():
        if task_result.successful():
            response["result"] = task_result.result
        else:
            response["error"] = str(task_result.result)
    
    return response

@router.post("/tasks/{task_id}/cancel", response_model=dict)
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel a running task
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Check if task exists and is not already finished
    if not task_result.ready():
        # Attempt to revoke the task
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "task_id": task_id,
            "status": "revoked",
            "message": "Task revocation requested"
        }
    else:
        return {
            "task_id": task_id,
            "status": task_result.status,
            "message": "Task already completed or failed, cannot be cancelled"
        }

@router.get("/tasks", response_model=dict)
async def get_active_tasks(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all active tasks (admin only)
    """
    # Get active tasks from all workers
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active() or {}
    scheduled_tasks = inspect.scheduled() or {}
    reserved_tasks = inspect.reserved() or {}
    
    # Format response
    response = {
        "active": [],
        "scheduled": [],
        "reserved": []
    }
    
    # Process active tasks
    for worker, tasks in active_tasks.items():
        for task in tasks:
            response["active"].append({
                "task_id": task.get("id"),
                "name": task.get("name"),
                "args": task.get("args"),
                "kwargs": task.get("kwargs"),
                "worker": worker,
                "time_start": task.get("time_start")
            })
    
    # Process scheduled tasks
    for worker, tasks in scheduled_tasks.items():
        for task in tasks:
            response["scheduled"].append({
                "task_id": task.get("request", {}).get("id"),
                "name": task.get("request", {}).get("name"),
                "args": task.get("request", {}).get("args"),
                "kwargs": task.get("request", {}).get("kwargs"),
                "worker": worker,
                "eta": task.get("eta")
            })
    
    # Process reserved tasks
    for worker, tasks in reserved_tasks.items():
        for task in tasks:
            response["reserved"].append({
                "task_id": task.get("id"),
                "name": task.get("name"),
                "args": task.get("args"),
                "kwargs": task.get("kwargs"),
                "worker": worker
            })
    
    return response 