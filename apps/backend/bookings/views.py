from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer
from services.models import Service
from payments.models import Currency

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_booking(request):
    """Allows a client to book a service"""
    user = request.user
    service_id = request.data.get("service_id")
    currency_code = request.data.get("currency_code")
    auto_renewal = request.data.get("auto_renewal", False)

    try:
        service = Service.objects.get(id=service_id)
        currency = Currency.objects.get(code=currency_code)
        total_price = service.price * currency.exchange_rate

        booking = Booking.objects.create(
            user=user, service=service, currency=currency, total_price=total_price, auto_renewal=auto_renewal
        )

        return Response({"message": "Booking successful", "booking_id": booking.id})

    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)
    except Currency.DoesNotExist:
        return Response({"error": "Invalid currency"}, status=400)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_booking_status(request, booking_id):
    """Admin can update booking status"""
    status = request.data.get("status")
    if status not in ["approved", "completed", "cancelled"]:
        return Response({"error": "Invalid status"}, status=400)

    try:
        booking = Booking.objects.get(id=booking_id)
        if request.user.is_superuser or request.user.is_staff:
            booking.status = status
            booking.save()
            return Response({"message": f"Booking updated to {status}"})
        return Response({"error": "Unauthorized"}, status=403)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_bookings(request):
    """Fetches all bookings for the logged-in user"""
    bookings = Booking.objects.filter(user=request.user)
    return Response({"bookings": BookingSerializer(bookings, many=True).data})
