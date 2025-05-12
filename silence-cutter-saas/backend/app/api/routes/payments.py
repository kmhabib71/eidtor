import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Body, status
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User, SubscriptionTier
from app.services.payment_service import (
    create_customer,
    create_subscription,
    cancel_subscription,
    handle_stripe_webhook
)

logger = logging.getLogger("silence-cutter")

router = APIRouter()

class SubscriptionRequest(BaseModel):
    payment_method_id: str
    subscription_tier: SubscriptionTier

class StripeWebhookPayload(BaseModel):
    payload: Dict[str, Any]

@router.post("/create-subscription", response_model=Dict[str, Any])
async def create_user_subscription(
    subscription_data: SubscriptionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a subscription for the current user
    """
    try:
        # Get or create Stripe customer
        customer_id = getattr(current_user, "stripe_customer_id", None)
        if not customer_id:
            customer_id = await create_customer(current_user)
        
        # Create subscription
        success, result = await create_subscription(
            user=current_user,
            customer_id=customer_id,
            tier=subscription_data.subscription_tier,
            payment_method_id=subscription_data.payment_method_id
        )
        
        if not success and result.get("status") == "requires_action":
            # Return client secret for 3D Secure authentication
            return {
                "requires_action": True,
                "client_secret": result.get("client_secret")
            }
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Subscription creation failed")
            )
        
        return {
            "success": True,
            "subscription": result
        }
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/cancel-subscription", response_model=Dict[str, Any])
async def cancel_user_subscription(
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel the current user's subscription
    """
    try:
        # Check if user has an active subscription
        if current_user.subscription_tier == SubscriptionTier.FREE:
            return {
                "message": "No active subscription to cancel"
            }
        
        result = await cancel_subscription(current_user)
        
        return {
            "success": True,
            "message": result.get("message"),
            "end_date": result.get("end_date")
        }
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/subscription-plans", response_model=Dict[str, Any])
async def get_subscription_plans():
    """
    Get available subscription plans
    """
    return {
        "plans": [
            {
                "id": SubscriptionTier.FREE,
                "name": "Free",
                "description": "Up to 1 hour of processing per month",
                "price": 0,
                "features": [
                    "Up to 1 hour of processing per month",
                    "720p max resolution",
                    "Basic silence removal"
                ]
            },
            {
                "id": SubscriptionTier.PRO,
                "name": "Pro",
                "description": "Up to 10 hours of processing per month",
                "price": 9.99,
                "features": [
                    "Up to 10 hours of processing per month",
                    "1080p max resolution",
                    "Advanced silence detection settings",
                    "Keep original files for 30 days"
                ]
            },
            {
                "id": SubscriptionTier.ENTERPRISE,
                "name": "Enterprise",
                "description": "Up to 50 hours of processing per month",
                "price": 29.99,
                "features": [
                    "Up to 50 hours of processing per month",
                    "4K resolution support",
                    "Advanced silence detection with AI",
                    "Keep original files for 90 days",
                    "Priority processing"
                ]
            }
        ]
    }

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Handle Stripe webhook events
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe signature is required"
        )
    
    try:
        # Get payload as bytes
        payload = await request.body()
        
        # Process webhook
        result = await handle_stripe_webhook(payload, stripe_signature)
        
        return {"status": "success", "event_processed": result.get("event_type")}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 