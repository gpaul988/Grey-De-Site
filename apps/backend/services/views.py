from rest_framework.decorators import api_view, permission_classes
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import ServiceBooking, Service, PaymentGateway, Payment

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_service(request):
    """User books a service and makes payment"""
    user = request.user
    service_id = request.data.get("service_id")
    amount = request.data.get("amount")
    currency = request.data.get("currency", "USD")
    gateway = request.data.get("gateway", PaymentGateway.PAYSTACK)
    scheduled_date = request.data.get("scheduled_date")

    service = Service.objects.get(id=service_id)

    payment = Payment.objects.create(
        user=user,
        amount=amount,
        currency=currency,
        gateway=gateway,
        reference=f"{user.id}-{now().timestamp()}",
        status="pending"
    )

    booking = ServiceBooking.objects.create(
        user=user,
        service=service,
        payment=payment,
        scheduled_date=scheduled_date
    )

    return Response({"message": "Booking created, proceed with payment", "booking_id": booking.id})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_service_status(request, booking_id):
    """Admins can update service progress"""
    status = request.data.get("status")

    if status not in ["pending", "in_progress", "completed", "canceled"]:
        return Response({"error": "Invalid status"}, status=400)

    try:
        booking = ServiceBooking.objects.get(id=booking_id)
        booking.status = status
        booking.save()
        return Response({"message": f"Service status updated to {status}"})
    except ServiceBooking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)