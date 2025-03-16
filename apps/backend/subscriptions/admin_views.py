from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from datetime import timedelta
from .models import Subscription

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_subscriptions(_request):
    """Admin view to list all subscriptions"""
    subscriptions = Subscription.objects.all()
    data = [
        {
            "user": sub.user.username,
            "plan": sub.plan.name,
            "expires": sub.end_date,
            "auto_renew": sub.auto_renew,
        }
        for sub in subscriptions
    ]
    return Response({"subscriptions": data})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def extend_subscription(_request):
    """Admin manually extends a user's subscription"""
    username = _request.data.get("username")
    days = _request.data.get("days")

    try:
        subscription = Subscription.objects.get(user__username=username)
        subscription.end_date += timedelta(days=days)
        subscription.save()
        return Response({"message": "Subscription extended successfully"})

    except Subscription.DoesNotExist:
        return Response({"error": "Subscription not found"}, status=404)