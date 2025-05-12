import logging
import stripe
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

from app.core.config import settings
from app.models.user import User, SubscriptionTier
from app.services.user_service import update_user

logger = logging.getLogger("silence-cutter")

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY

# Subscription plan IDs (these would be created in Stripe dashboard)
SUBSCRIPTION_PLANS = {
    SubscriptionTier.FREE: None,  # Free tier doesn't have a Stripe plan
    SubscriptionTier.PRO: "price_pro_monthly",  # Replace with actual Stripe price ID
    SubscriptionTier.ENTERPRISE: "price_enterprise_monthly"  # Replace with actual Stripe price ID
}

# Processing minutes limits by tier
PROCESSING_LIMITS = {
    SubscriptionTier.FREE: 60,  # 1 hour per month
    SubscriptionTier.PRO: 600,  # 10 hours per month
    SubscriptionTier.ENTERPRISE: 3000  # 50 hours per month
}

async def create_customer(user: User) -> str:
    """
    Create a Stripe customer for a user
    """
    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={
                "user_id": user.id
            }
        )
        
        # Update user with customer ID
        await update_user(user.id, {"stripe_customer_id": customer.id})
        
        return customer.id
    except Exception as e:
        logger.error(f"Error creating Stripe customer: {str(e)}")
        raise

async def create_subscription(
    user: User,
    customer_id: str,
    tier: SubscriptionTier,
    payment_method_id: str
) -> Tuple[bool, Dict[str, Any]]:
    """
    Create a subscription for a user
    """
    if tier == SubscriptionTier.FREE:
        # Free tier doesn't need a Stripe subscription
        await update_user(
            user.id,
            {
                "subscription_tier": SubscriptionTier.FREE,
                "subscription_end_date": None,
                "processing_minutes_limit": PROCESSING_LIMITS[SubscriptionTier.FREE]
            }
        )
        return True, {"message": "Switched to free tier successfully"}
    
    try:
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )
        
        # Set as default payment method
        stripe.Customer.modify(
            customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            }
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {"price": SUBSCRIPTION_PLANS[tier]}
            ],
            expand=["latest_invoice.payment_intent"]
        )
        
        # If payment requires additional action
        if subscription.status == "incomplete" and subscription.latest_invoice.payment_intent:
            payment_intent = subscription.latest_invoice.payment_intent
            if payment_intent.status == "requires_action":
                return False, {
                    "subscription_id": subscription.id,
                    "client_secret": payment_intent.client_secret,
                    "status": "requires_action"
                }
        
        # If subscription is active or trialing
        if subscription.status in ["active", "trialing"]:
            # Calculate end date (for billing cycle)
            end_date = datetime.fromtimestamp(subscription.current_period_end)
            
            # Update user with new subscription info
            await update_user(
                user.id,
                {
                    "subscription_tier": tier,
                    "stripe_subscription_id": subscription.id,
                    "subscription_end_date": end_date,
                    "processing_minutes_limit": PROCESSING_LIMITS[tier]
                }
            )
            
            return True, {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end
            }
        
        # If subscription failed
        return False, {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "error": "Subscription creation failed"
        }
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise

async def cancel_subscription(user: User) -> Dict[str, Any]:
    """
    Cancel a user's subscription
    """
    try:
        # Get stripe_subscription_id from user (would be stored in user metadata)
        stripe_subscription_id = user.stripe_subscription_id
        
        if not stripe_subscription_id:
            return {"message": "No active subscription to cancel"}
        
        # Cancel subscription at period end
        subscription = stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update user record
        # Note: We don't downgrade immediately, it remains until the end of the billing period
        await update_user(
            user.id,
            {
                "subscription_end_date": datetime.fromtimestamp(subscription.current_period_end)
            }
        )
        
        return {
            "message": "Subscription will be cancelled at the end of the billing period",
            "end_date": subscription.current_period_end
        }
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise

async def handle_stripe_webhook(payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
    """
    Handle Stripe webhook events
    """
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle different event types
        if event.type == "customer.subscription.updated":
            subscription = event.data.object
            await handle_subscription_updated(subscription)
        
        elif event.type == "customer.subscription.deleted":
            subscription = event.data.object
            await handle_subscription_deleted(subscription)
        
        elif event.type == "invoice.payment_succeeded":
            invoice = event.data.object
            await handle_payment_succeeded(invoice)
        
        elif event.type == "invoice.payment_failed":
            invoice = event.data.object
            await handle_payment_failed(invoice)
        
        return {"status": "success", "event_type": event.type}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise

async def handle_subscription_updated(subscription: Dict[str, Any]) -> None:
    """
    Handle subscription updated event
    """
    # Get customer ID and find associated user
    customer_id = subscription.get("customer")
    # We would need a way to find user by Stripe customer ID
    # This is a mock implementation
    
    # Update subscription details
    end_date = datetime.fromtimestamp(subscription.get("current_period_end"))
    
    # We could update user subscription status here
    logger.info(f"Subscription {subscription.get('id')} updated, ends on {end_date}")

async def handle_subscription_deleted(subscription: Dict[str, Any]) -> None:
    """
    Handle subscription deleted event
    """
    # Get customer ID and find associated user
    customer_id = subscription.get("customer")
    # We would need a way to find user by Stripe customer ID
    
    # Downgrade user to free tier
    # We could implement this with a function to find user by Stripe customer ID
    # and then update their subscription tier
    logger.info(f"Subscription {subscription.get('id')} deleted")

async def handle_payment_succeeded(invoice: Dict[str, Any]) -> None:
    """
    Handle payment succeeded event
    """
    # Get customer ID and find associated user
    customer_id = invoice.get("customer")
    # We would need a way to find user by Stripe customer ID
    
    logger.info(f"Payment succeeded for invoice {invoice.get('id')}")

async def handle_payment_failed(invoice: Dict[str, Any]) -> None:
    """
    Handle payment failed event
    """
    # Get customer ID and find associated user
    customer_id = invoice.get("customer")
    # We would need a way to find user by Stripe customer ID
    
    # We could send notification to user about payment failure
    logger.warning(f"Payment failed for invoice {invoice.get('id')}") 