from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import ServiceBooking

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_service(request):
    """Book a service and initiate payment."""
    user = request.user
    service = request.data.get("service")
    price = request.data.get("price")
    currency = request.data.get("currency", "USD")

    if not service or not price:
        return Response({"error": "Service and price required"}, status=400)

    booking = ServiceBooking.objects.create(user=user, service=service, price=price, currency=currency)

    return Response({"message": "Service booked successfully!", "booking_id": booking.id})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_service_status(request):
    """Admin updates service completion status"""
    booking_id = request.data.get("booking_id")
    status = request.data.get("status")  # 'in_progress', 'completed', 'canceled'

    booking = get_object_or_404(ServiceBooking, id=booking_id)

    if status == "completed":
        booking.status = "completed"
        booking.completed_at = now()
    elif status in ["in_progress", "canceled"]:
        booking.status = status
    else:
        return Response({"error": "Invalid status"}, status=400)

    booking.save()
    return Response({"message": f"Service status updated to {status}"})
