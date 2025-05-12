import logging
import asyncio
from typing import Dict, Any
from celery import Task
from datetime import datetime

from app.core.celery_app import celery_app
from app.services.user_service import get_all_users, update_user

logger = logging.getLogger("silence-cutter")

class AsyncTask(Task):
    """Task that runs an async function in an event loop."""
    
    def run_async(self, coro):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

@celery_app.task(bind=True, base=AsyncTask)
def reset_monthly_usage_task(self) -> Dict[str, Any]:
    """
    Reset monthly usage for all users (scheduled to run monthly)
    """
    try:
        # Get all users
        users = self.run_async(get_all_users(skip=0, limit=1000))
        
        reset_count = 0
        for user in users:
            # Only reset if usage > 0
            if user.processing_minutes_used > 0:
                # Update user with reset usage
                self.run_async(
                    update_user(
                        user_id=user.id,
                        user_update={"processing_minutes_used": 0}
                    )
                )
                reset_count += 1
        
        return {
            "status": "success",
            "reset_count": reset_count,
            "total_users": len(users)
        }
    
    except Exception as e:
        logger.error(f"Error in reset_monthly_usage_task: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@celery_app.task(bind=True, base=AsyncTask)
def check_subscription_expiry_task(self) -> Dict[str, Any]:
    """
    Check for expired subscriptions and downgrade to free tier
    """
    try:
        # Get all users
        users = self.run_async(get_all_users(skip=0, limit=1000))
        
        now = datetime.utcnow()
        expired_count = 0
        
        for user in users:
            # Check if subscription has expired
            if (user.subscription_tier != "free" and 
                user.subscription_end_date and 
                user.subscription_end_date < now):
                
                # Downgrade to free tier
                self.run_async(
                    update_user(
                        user_id=user.id,
                        user_update={
                            "subscription_tier": "free",
                            "processing_minutes_limit": 60  # Reset to free tier limit
                        }
                    )
                )
                expired_count += 1
        
        return {
            "status": "success",
            "expired_count": expired_count,
            "total_users": len(users)
        }
    
    except Exception as e:
        logger.error(f"Error in check_subscription_expiry_task: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        } 