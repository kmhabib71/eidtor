import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User, UserUpdate
from app.services.user_service import get_user_by_id, update_user, delete_user

logger = logging.getLogger("silence-cutter")

router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile
    """
    return current_user

@router.patch("/me", response_model=User)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile
    """
    updated_user = await update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )
    
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Delete current user
    """
    success = await delete_user(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return None

@router.get("/usage", response_model=dict)
async def get_usage_stats(current_user: User = Depends(get_current_active_user)):
    """
    Get usage statistics for the current user
    """
    return {
        "processing_minutes_used": current_user.processing_minutes_used,
        "processing_minutes_limit": current_user.processing_minutes_limit,
        "usage_percentage": (current_user.processing_minutes_used / current_user.processing_minutes_limit * 100) 
            if current_user.processing_minutes_limit > 0 else 0,
        "subscription_tier": current_user.subscription_tier,
        "subscription_end_date": current_user.subscription_end_date
    } 