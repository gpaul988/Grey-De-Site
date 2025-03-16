from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.timezone import now, timedelta
from datetime import datetime
from .models import SubscriptionPlan, UserSubscription, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from django.core.mail import send_mail
import requests
from decimal import Decimal
from django.conf import settings


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_subscriptions(request):
    """Admin view to get all active subscriptions"""
    subscriptions = UserSubscription.objects.all().values('user__email', 'plan__name', 'status', 'end_date')
    return Response(subscriptions)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def cancel_user_subscription(request):
    """Admin cancels a user’s subscription"""
    user_id = request.data.get("user_id")
    try:
        subscription = UserSubscription.objects.get(user_id=user_id, status="active")
        subscription.status = "expired"
        subscription.save()
        return Response({"message": "Subscription cancelled."})
    except UserSubscription.DoesNotExist:
        return Response({"error": "Subscription not found."}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_subscription(request):
    """Handles subscription upgrade requests."""
    user = request.user
    new_plan_id = request.data.get("new_plan_id")

    new_plan = get_object_or_404(SubscriptionPlan, id=new_plan_id)
    user_subscription = get_object_or_404(UserSubscription, user=user)

    if new_plan.price >= user_subscription.plan.price:
        return Response({"error": "Cannot downgrade to a higher or same plan."}, status=400)

    # Calculate price difference
    days_remaining = (user_subscription.end_date - now()).days
    old_plan_daily_rate = Decimal(user_subscription.plan.price) / Decimal(user_subscription.plan.duration)
    old_plan_value_remaining = old_plan_daily_rate * Decimal(days_remaining)
    new_plan_daily_rate = Decimal(new_plan.price) / Decimal(new_plan.duration) if new_plan.duration > 0 else Decimal(0)
    new_plan_total_cost = Decimal(new_plan.price) + (new_plan_daily_rate * Decimal(new_plan.grace_period))
    upgrade_cost = max(new_plan_total_cost - old_plan_value_remaining, Decimal(0))

    if upgrade_cost == 0:
        return Response({"message": "No additional cost. Upgrading for free."})

    reference = f"upgrade_{user.id}_{now().timestamp()}"

    # Charge the user for upgrade cost
    response = requests.post(
        f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
        headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
        json={
            "email": user.email,
            "amount": int(upgrade_cost * 100),  # Convert to kobo
            "reference": reference,
        },
    )

    data = response.json()
    if response.status_code == 200 and data["status"] == "success":
        user_subscription.plan = new_plan
        user_subscription.end_date = now() + timedelta(days=new_plan.duration)
        user_subscription.save()
        return Response({"message": "Subscription upgraded successfully!"})
    else:
        return Response({"error": "Upgrade failed. Please try again."}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def downgrade_subscription(request):
    """Handles subscription downgrade requests."""
    user = request.user
    new_plan_id = request.data.get("new_plan_id")

    new_plan = get_object_or_404(SubscriptionPlan, id=new_plan_id)
    user_subscription = get_object_or_404(UserSubscription, user=user)

    if new_plan.price >= user_subscription.plan.price:
        return Response({"error": "Cannot downgrade to a higher or same plan."}, status=400)

    # Calculate refund amount
    days_remaining = (user_subscription.end_date - now()).days
    old_plan_daily_rate = Decimal(user_subscription.plan.price) / Decimal(user_subscription.plan.duration)
    old_plan_value_remaining = old_plan_daily_rate * Decimal(days_remaining)
    new_plan_total_cost = Decimal(new_plan.price)
    refund_amount = max(old_plan_value_remaining - new_plan_total_cost, Decimal(0))

    # Refund through Paystack
    if refund_amount > 0:
        refund_response = requests.post(
            f"{settings.PAYSTACK_BASE_URL}/refund",
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            json={"transaction": user_subscription.payment_reference, "amount": int(refund_amount * 100)}
        )
        if refund_response.status_code != 200:
            return Response({"error": "Refund processing failed."}, status=400)

    user_subscription.plan = new_plan
    user_subscription.end_date = now() + timedelta(days=new_plan.duration)
    user_subscription.save()

    return Response({"message": f"Subscription downgraded successfully! Refund: ${refund_amount}"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_history(request):
    """Retrieve user's past and current subscriptions."""
    user = request.user
    history = UserSubscription.objects.filter(user=user).values('plan__name', 'status', 'start_date', 'end_date')
    return Response(history)


@api_view(['GET'])
def list_subscription_plans(request):
    """Get all available subscription plans"""
    plans = SubscriptionPlan.objects.all()
    serializer = SubscriptionPlanSerializer(plans, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscription(request):
    """Get the current user's subscription details"""
    subscription = Subscription.objects.filter(user=request.user).first()
    if not subscription:
        return Response({"error": "No active subscription found"}, status=404)

    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notify_users():
    """Send notifications for expiring subscriptions"""
    today = now().date()
    expiring_subscriptions = Subscription.objects.filter(
        status="active",
        end_date__lte=today + timedelta(days=60)  # Check for subscriptions expiring within the next 60 days
    )

    for subscription in expiring_subscriptions:
        days_to_expiry = (subscription.end_date - today).days

        if subscription.plan.duration == 7:  # weekly subscription
            if days_to_expiry <= 3:
                send_mail(
                    subject="Your Subscription is Expiring Soon",
                    message=f"Dear {subscription.user.username},\n\nYour subscription for {subscription.plan.name} is expiring on {subscription.end_date}. Please renew it to avoid service interruption.",
                    from_email="support@greyinfotech.com.ng",
                    recipient_list=[subscription.user.email],
                )
        elif subscription.plan.duration == 30:  # Monthly subscription
            if days_to_expiry <= 7:
                send_mail(
                    subject="Your Subscription is Expiring Soon",
                    message=f"Dear {subscription.user.username},\n\nYour subscription for {subscription.plan.name} is expiring on {subscription.end_date}. Please renew it to avoid service interruption.",
                    from_email="support@greyinfotech.com.ng",
                    recipient_list=[subscription.user.email],
                )
        elif subscription.plan.duration == 365:  # Yearly subscription
            if days_to_expiry <= 60 and days_to_expiry % 3 == 0:  # Twice a week for the last 2 months
                send_mail(
                    subject="Your Subscription is Expiring Soon",
                    message=f"Dear {subscription.user.username},\n\nYour subscription for {subscription.plan.name} is expiring on {subscription.end_date}. Please renew it to avoid service interruption.",
                    from_email="support@greyinfotech.com.ng",
                    recipient_list=[subscription.user.email],
                )

    return Response({"message": "Notifications sent successfully!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_subscription(request):
    """Get the current user's subscription details"""
    subscription = Subscription.objects.filter(user=request.user).first()
    if not subscription:
        return Response({"error": "No active subscription found"}, status=404)

    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase_subscription(request):
    """Allow users to purchase a subscription plan"""
    plan_id = request.data.get("plan_id")
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        end_date = datetime.now() + timedelta(days=plan.duration)

        Subscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=end_date
        )
        return Response({"message": "Subscription activated successfully"})

    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=404)