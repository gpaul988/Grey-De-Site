import random
import string
import requests
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from models import  Subscription, Payment, RefundRequest, PaymentGateway
from serializers import SubscriptionSerializer, PaymentSerializer
from authentication.permissions import IsSuperAdmin, IsAdminUser, IsAuthenticated
from apps.backend.subscriptions.models import SubscriptionPlan, UserSubscription
from backend.utils.email_utils import send_payment_notification

def generate_reference(length=10):
    """Generate a unique payment reference"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """Initiate a payment and get a gateway URL."""
    user = request.user
    amount = request.data.get("amount")
    currency = request.data.get("currency", "USD")
    gateway = request.data.get("gateway", "paystack")

    if not amount or float(amount) <= 0:
        return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

    reference = generate_reference()
    payment = Payment.objects.create(user=user, amount=amount, currency=currency, gateway=gateway, reference=reference)

    # Mock payment URL generation
    payment_url = f"https://{gateway}.com/pay?amount={amount}&currency={currency}&reference={reference}"

    return Response({"payment_url": payment_url, "reference": reference})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_payment(request, reference):
    """Verify payment status."""
    payment = get_object_or_404(Payment, reference=reference)

    # Mock verification (In real cases, call the gateway's API)
    payment.status = "successful"
    payment.save()

    return Response({"message": "Payment verified successfully", "status": payment.status})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_subscription_payment(request):
    """Verify payment and activate subscription"""
    reference = request.data.get("reference")
    plan_name = request.data.get("plan")  # Plan name: 'basic', 'premium', 'enterprise'

    # Fetch plan
    try:
        plan = SubscriptionPlan.objects.get(name=plan_name)
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Invalid plan"}, status=status.HTTP_400_BAD_REQUEST)

    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and data["data"]["status"] == "success":
        user = request.user
        end_date = now() + timedelta(days=plan.duration)

        # Create or update subscription
        subscription, created = UserSubscription.objects.update_or_create(
            user=user,
            defaults={"plan": plan, "start_date": now(), "end_date": end_date},
        )

        return Response({"message": "Subscription activated successfully!"})

    return Response({"error": "Payment verification failed!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def paystack_verify_payment(request):
    """Verify payment and send email notification"""
    reference = request.data.get("reference")
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and data["data"]["status"] == "success":
        user = request.user
        amount = data["data"]["amount"] / 100  # Convert from kobo

        # Send email notification
        send_payment_notification(
            user.email,
            "Payment Successful!",
            f"Dear {user.first_name},\n\nYour payment of ₦{amount} was successful. Thank you for using Grey Infotech services!\n\nBest Regards,\nGrey Infotech Team"
        )

        return Response({"message": "Payment verified successfully!"})

    return Response({"error": "Payment verification failed!"}, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsSuperAdmin]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def paystack_initialize_payment(request):
    """Initialize a Paystack payment session"""
    user = request.user
    amount = request.data.get("amount")  # Amount in kobo (100 NGN = 10000 kobo)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": user.email,
        "amount": amount,
        "callback_url": request.build_absolute_uri('/payment/success/')
    }

    response = requests.post(f"{settings.PAYSTACK_BASE_URL}/transaction/initialize", headers=headers, json=data)

    if response.status_code == 200:
        return Response(response.json())
    return Response(response.json(), status=response.status_code)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flutterwave_initialize_payment(request):
    """Initialize a Flutterwave payment session"""
    user = request.user
    amount = request.data.get("amount")  # Amount in Naira

    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "tx_ref": f"{user.id}-{amount}",
        "amount": amount,
        "currency": "NGN",
        "redirect_url": request.build_absolute_uri('/payment/success/'),
        "customer": {
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}",
        }
    }

    response = requests.post(f"{settings.FLUTTERWAVE_BASE_URL}/payments", headers=headers, json=data)

    if response.status_code == 200:
        return Response(response.json())
    return Response(response.json(), status=response.status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_refund(request):
    """Allow users to request a refund"""
    user = request.user
    reference = request.data.get("reference")
    reason = request.data.get("reason")

    payment = get_object_or_404(Payment, reference=reference, user=user)

    if payment.status != "successful":
        return Response({"error": "Only successful payments can be refunded"}, status=400)

    if RefundRequest.objects.filter(payment=payment).exists():
        return Response({"error": "Refund request already exists"}, status=400)

    refund_request = RefundRequest.objects.create(user=user, payment=payment, reason=reason)

    return Response({"message": "Refund request submitted", "refund_id": refund_request.id})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def process_refund(request):
    """Admin approves or denies a refund"""
    refund_id = request.data.get("refund_id")
    action = request.data.get("action")  # 'approve' or 'deny'

    refund_request = get_object_or_404(RefundRequest, id=refund_id)

    if action == "approve":
        refund_request.status = "approved"
        refund_request.reviewed_at = now()
        refund_request.save()

        # Update payment status
        refund_request.payment.status = "refunded"
        refund_request.payment.refunded_at = now()
        refund_request.payment.save()

        return Response({"message": "Refund approved successfully!"})

    elif action == "deny":
        refund_request.status = "denied"
        refund_request.reviewed_at = now()
        refund_request.save()
        return Response({"message": "Refund request denied!"})

    return Response({"error": "Invalid action"}, status=400)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """Creates a new payment with selected currency & gateway"""
    user = request.user
    amount = request.data.get("amount")
    currency = request.data.get("currency", "USD")
    gateway = request.data.get("gateway", PaymentGateway.PAYSTACK)

    if gateway not in [choice[0] for choice in PaymentGateway.choices]:
        return Response({"error": "Invalid payment gateway"}, status=400)

    payment = Payment.objects.create(
        user=user,
        amount=amount,
        currency=currency,
        gateway=gateway,
        reference=f"{user.id}-{now().timestamp()}-{random.randint(1000,9999)}",
        status="pending"
    )

    return Response(PaymentSerializer(payment).data)