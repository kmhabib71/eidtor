import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from app.core.dependencies import get_current_admin_user
from app.models.user import User, UserUpdate
from app.services.user_service import get_all_users, get_user_by_id, update_user, delete_user
from app.tasks.user_tasks import reset_monthly_usage_task, check_subscription_expiry_task

logger = logging.getLogger("silence-cutter")

router = APIRouter()

@router.get("/users", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    email: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all users (admin only)
    """
    users = await get_all_users(skip=skip, limit=limit)
    
    # Filter by email if provided
    if email:
        users = [user for user in users if email.lower() in user.email.lower()]
    
    return users

@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific user by ID (admin only)
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.patch("/users/{user_id}", response_model=User)
async def update_user_admin(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a user (admin only)
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )
    
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a user (admin only)
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting self
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account from admin API"
        )
    
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return None

@router.post("/tasks/reset-monthly-usage", response_model=dict)
async def run_reset_monthly_usage(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Run the task to reset monthly usage for all users (admin only)
    """
    task = reset_monthly_usage_task.delay()
    
    return {
        "message": "Reset monthly usage task started",
        "task_id": task.id
    }

@router.post("/tasks/check-subscription-expiry", response_model=dict)
async def run_check_subscription_expiry(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Run the task to check for expired subscriptions (admin only)
    """
    task = check_subscription_expiry_task.delay()
    
    return {
        "message": "Check subscription expiry task started",
        "task_id": task.id
    } 