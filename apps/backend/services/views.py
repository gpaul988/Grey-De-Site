from django.utils.timezone import now, timedelta
from .utils import process_payment_refund
from rest_framework.response import Response
from .llm_analysis import analyze_file_content
from .serializers import ServiceBookingSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import ServiceBooking, Service, PaymentGateway, Payment, UploadedFile


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
        user=request.user,
        service=service,
        payment=payment,
        status="pending",
        scheduled_date=scheduled_date
    )

    return Response({"message": "Booking created, proceed with payment", "booking_id": booking.id})

@api_view(["POST"])
def book_service_with_estimate(request):
    """Allows users to book a service and get estimated completion time"""
    user = request.user
    service_name = request.data.get("service_name")
    currency = request.data.get("currency", "USD").upper()

    # Define estimated delivery times (mock logic)
    service_time_estimates = {
        "Web Development": 84,  # days
        "Mobile App Development": 224,
        "Blockchain Development": 330,
        "Web Design": 63,
        "Web App Development": 126,
        "Wix Development": 56,
        "WordPress Development": 57,
        "AI Development": 504,
        "Android Development": 224,
        "Cross Platform Development": 330,
        "Flutter Development": 220,
        "iOS Development": 220,
        "Vue.js Development": 220,
        "Squarespace Development": 56,
        "Shopify Development": 220,
        "React Development": 220,
        "PHP Development": 170,
        "Next.js Development": 220,
        "Node.js Development": 220,
        "Laravel Development": 200,
        "Drupal Development": 100,
        "Joomla Development": 60,
        "CMS Development": 330,
        "Angular Development": 240,
        "Python Development": 240,
        "Django Development": 240,
        "Ruby on Rails Development": 200,
        "Mac Software Development": 330,
        "React Native Development": 250,
        "Software Development": 356,
        "Windows Software Development": 330,
        "App Store Optimization": 36,
        "SEO": 20,
        "Social Media Marketing": 15,
        "Ecommerce Development": 68,
    }

    try:
        estimated_time = service_time_estimates.get(service_name, 14)
        completion_date = now() + timedelta(days=estimated_time)

        service = ServiceBooking.objects.create(
            user=user, service_name=service_name, expected_completion_date=completion_date
        )

        return Response({
            "message": f"Service '{service_name}' booked successfully in {currency}",
            "expected_completion": completion_date.strftime("%Y-%m-%d"),
            "service_id": service.id
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_bookings(request):
    """Retrieve all bookings for the logged-in user"""
    bookings = ServiceBooking.objects.filter(user=request.user).values("service__name", "status", "scheduled_date")
    return Response({"bookings": list(bookings)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def track_service(request):
    """Allows users to track the status of their booked services"""
    user = request.user
    services = ServiceBooking.objects.filter(user=user)

    service_data = [
        {
            "service_name": service.service_name,
            "status": service.status,
            "expected_completion": service.expected_completion_date,
        }
        for service in services
    ]

    return Response(service_data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_service_status(request):
    """Allows admins to update the status of a booked service"""
    service_id = request.data.get("service_id")
    new_status = request.data.get("status").lower()

    try:
        service = ServiceBooking.objects.get(id=service_id)

        if new_status in ["pending", "in_progress", "completed", "cancelled"]:
            service.status = new_status
            service.save()
            return Response({"message": "Service status updated"})
        return Response({"error": "Invalid status"}, status=400)

    except ServiceBooking.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_service_progress(request):
    """Users or admins can update service progress"""
    service_id = request.data.get("service_id")
    new_progress = int(request.data.get("progress"))

    try:
        service = Service.objects.get(id=service_id, user=request.user)

        if new_progress < service.progress:
            return Response({"error": "Progress cannot decrease"}, status=400)

        service.update_progress(new_progress)
        return Response({"message": "Progress updated successfully"})

    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_all_bookings(request):
    """Fetch all service bookings (Admin only)"""
    bookings = ServiceBooking.objects.all()
    serializer = ServiceBookingSerializer(bookings, many=True)
    return Response({"bookings": serializer.data})

@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_booking_status(request, booking_id):
    """Update service booking status (Admin only)"""
    try:
        booking = ServiceBooking.objects.get(id=booking_id)
        new_status = request.data.get("status")

        if new_status not in ["pending", "in_progress", "completed", "cancelled"]:
            return Response({"error": "Invalid status"}, status=400)

        booking.status = new_status
        booking.save()
        return Response({"message": "Booking updated successfully"})

    except ServiceBooking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def process_refund(request):
    """Admins can issue refunds for incomplete/canceled services"""
    service_id = request.data.get("service_id")

    try:
        service = Service.objects.get(id=service_id)

        if service.status == "completed":
            return Response({"error": "Cannot refund a completed service"}, status=400)

        if service.payment_status == "refunded":
            return Response({"error": "Service already refunded"}, status=400)

        # Process refund via Paystack, Flutterwave, or other payment gateways
        refund_successful = process_payment_refund(service)

        if refund_successful:
            service.payment_status = "refunded"
            service.status = "canceled"
            service.save()
            return Response({"message": "Refund issued successfully"})
        else:
            return Response({"error": "Refund failed"}, status=500)

    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """Handles client file uploads for LLM analysis"""
    file = request.FILES.get("file")

    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    uploaded_file = UploadedFile.objects.create(user=request.user, file=file)

    # Trigger LLM analysis
    analysis_result = analyze_file_content(uploaded_file.file.path)
    uploaded_file.analysis_result = analysis_result
    uploaded_file.save()

    return Response({"message": "File uploaded successfully", "analysis": analysis_result})

