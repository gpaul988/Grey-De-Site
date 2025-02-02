from rest_framework.response import Response
from apps.backend.subscriptions.models import UserSubscription

def check_subscription(user, required_plan):
    """Check if a user has the required subscription plan"""
    try:
        subscription = UserSubscription.objects.get(user=user)
        return subscription.is_active() and subscription.plan.name == required_plan
    except UserSubscription.DoesNotExist:
        return False

def subscription_required(required_plan):
    """Decorator to restrict views based on subscription"""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_subscription(request.user, required_plan):
                return Response({"error": "Access restricted. Upgrade your plan!"}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
