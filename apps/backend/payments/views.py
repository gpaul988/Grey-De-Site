import random
import string
import logging
import requests
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from bookings.models import Booking
from rest_framework.response import Response
from rest_framework import status
from notifications.models import Notification
from services.models import ServiceBooking
from .models import Payment, RefundRequest, PaymentGateway, Invoice, Currency, CurrencyExchangeRate
from .serializers import SubscriptionSerializer, PaymentSerializer
from authentication.permissions import IsSuperAdmin, IsAdminUser, IsAuthenticated
from subscriptions.models import SubscriptionPlan, UserSubscription, Subscription
from backend.utils.email_utils import send_payment_notification

logger = logging.getLogger(__name__)
API_URL = "https://api.exchangerate-api.com/v6/latest/USD"

@api_view(["GET"])
def update_exchange_rates(request):
    """Fetch latest exchange rates from external API"""
    response = requests.get(API_URL)
    data = response.json()

    if "rates" in data:
        for currency, rate in data["rates"].items():
            obj, created = CurrencyExchangeRate.objects.update_or_create(
                currency_code=currency, defaults={"exchange_rate": rate, "last_updated": now()}
            )
            if created:
                print(f"Created new exchange rate for {currency}")
            else:
                print(f"Updated exchange rate for {currency}")

    return Response({"message": "Exchange rates updated successfully"})

PAYMENT_PROVIDERS = {
    "paystack": "https://api.paystack.co/transaction/initialize",
    "flutterwave": "https://api.flutterwave.com/v3/payments",
}

def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another using AbokiFX API"""
    url = "https://abokifx.com/api/v1/rates/movement"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {YOUR_AUTH_TOKEN}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    rates = data.get("rates", {})
    from_rate = rates.get(from_currency)
    to_rate = rates.get(to_currency)

    if from_rate and to_rate:
        conversion_rate = to_rate / from_rate
        return amount * conversion_rate
    else:
        raise ValueError(f"Conversion rate for {from_currency} or {to_currency} not found.")

def generate_reference(length=10):
    """Generate a unique payment reference"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """Initiates a payment through the selected provider"""
    user = request.user
    booking_id = request.data.get("booking_id")
    provider = request.data.get("provider").lower()

    if provider not in PAYMENT_PROVIDERS:
        return Response({"error": "Invalid payment provider"}, status=400)

    try:
        booking = Booking.objects.get(id=booking_id, user=user)
        transaction_id = f"{provider}_{user.id}_{booking.id}"
        payment = Payment.objects.create(
            user=user, booking=booking, provider=provider, transaction_id=transaction_id,
            amount=booking.total_price, currency=booking.currency.code, status="pending"
        )

        # Payment request payload
        payload = {
            "amount": float(payment.amount) * 100,  # Convert to minor units
            "currency": payment.currency,
            "reference": payment.transaction_id,
            "email": user.email,
            "callback_url": f"{settings.FRONTEND_URL}/payment-success",
        }

        # Headers for authentication
        headers = {"Authorization": f"Bearer {settings.PAYMENT_KEYS[provider]}"}

        # Send payment request
        response = requests.post(PAYMENT_PROVIDERS[provider], json=payload, headers=headers)
        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response({"error": "Payment failed"}, status=400)

    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

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

        if created:
            # Logic for when a new subscription is created
            print("A new subscription was created.")
        else:
            # Logic for when an existing subscription is updated
            print("An existing subscription was updated.")

        # You can also use the subscription object for further processing
        print(f"Subscription details: {subscription.plan}, {subscription.start_date}, {subscription.end_date}")

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
    """Allows users to request a refund for a recent payment"""
    user = request.user
    transaction_id = request.data.get("transaction_id")
    reason = request.data.get("reason")

    try:
        payment = Payment.objects.get(transaction_id=transaction_id, user=user)

        # Only allow refund requests for payments within the last 7 days
        if payment.created_at < now() - timedelta(days=7):
            return Response({"error": "Refund request period expired"}, status=400)

        if RefundRequest.objects.filter(payment=payment).exists():
            return Response({"error": "Refund already requested"}, status=400)

        refund = RefundRequest.objects.create(user=user, payment=payment, reason=reason)
        return Response({"message": "Refund request submitted", "refund_id": refund.id})

    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

@api_view(["POST"])
def process_payment(request):
    """Handles payments with multi-currency support"""
    user = request.user
    service_id = request.data.get("service_id")
    currency = request.data.get("currency", "USD").upper()

    try:
        service = ServiceBooking.objects.get(id=service_id, user=user)
        exchange_rate = CurrencyExchangeRate.objects.get(currency_code=currency).exchange_rate
        converted_price = float(service.price) * float(exchange_rate)

        # Process payment with selected gateway
        transaction = Payment.objects.create(
            user=user, service=service, amount=converted_price, currency=currency, status="pending"
        )

        return Response({"message": "Payment initiated", "converted_price": converted_price, "transaction": PaymentSerializer(transaction).data})

    except ServiceBooking.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)
    except CurrencyExchangeRate.DoesNotExist:
        return Response({"error": "Invalid currency"}, status=400)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def process_refund(request):
    """Allows admins to approve or reject refunds"""
    refund_id = request.data.get("refund_id")
    action = request.data.get("action").lower()  # "approve" or "reject"

    try:
        refund = RefundRequest.objects.get(id=refund_id)

        if refund.status != "pending":
            return Response({"error": "Refund already processed"}, status=400)

        if action == "approve":
            refund.status = "approved"
            refund.processed_at = now()
            refund.payment.status = "refunded"
            refund.payment.save()

            return Response({"message": "Refund approved"})
        elif action == "reject":
            refund.status = "rejected"
            refund.processed_at = now()
            return Response({"message": "Refund rejected"})

        return Response({"error": "Invalid action"}, status=400)

    except RefundRequest.DoesNotExist:
        return Response({"error": "Refund request not found"}, status=404)

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

@receiver(post_save, sender=Payment)
def create_invoice(sender, instance, created, **kwargs):
    """Generate an invoice with the selected currency"""
    if created and instance.status == "successful":
        Invoice.objects.create(
            user=instance.user,
            payment=instance,
            service=instance.service,
            total_amount=instance.amount,
            currency=instance.currency,  # Store currency in invoice
            due_date=instance.created_at + timedelta(days=30)
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_invoices(request):
    """Retrieve all invoices for the logged-in user"""
    invoices = Invoice.objects.filter(user=request.user).values("invoice_number", "total_amount", "issued_at", "due_date")
    return Response({"invoices": list(invoices)})

@receiver(post_save, sender=Payment)
def notify_payment_success(sender, instance, created, **kwargs):
    """Notify user when a payment is successful"""
    if created and instance.status == "successful":
        Notification.objects.create(user=instance.user, message=f"Your payment of ${instance.amount} was successful.")

@receiver(post_save, sender=RefundRequest)
def notify_refund_status(sender, instance, **kwargs):
    """Notify user about refund approval or rejection"""
    if instance.status == "approved":
        Notification.objects.create(user=instance.user, message="Your refund has been approved and processed.")
    elif instance.status == "rejected":
        Notification.objects.create(user=instance.user, message="Your refund request has been rejected.")

@receiver(post_save, sender=ServiceBooking)
def notify_service_update(sender, instance, **kwargs):
    """Notify user when service status is updated"""
    Notification.objects.create(user=instance.user, message=f"Your service '{instance.service.name}' is now {instance.status}.")

@api_view(["GET"])
def get_currency_exchange_rate(request, from_currency, to_currency):
    """Fetch currency conversion rate from external API"""
    try:
        conversion_rate = convert_currency(1, from_currency, to_currency)  # Convert 1 unit
        return Response({"rate": conversion_rate})
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_currencies(request):
    """Returns available currencies"""
    currencies = Currency.objects.all().values("name", "code", "symbol", "exchange_rate")
    return Response({"currencies": list(currencies)})

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_payments_overview(request):
    """Fetches all payments for admin review"""
    payments = Payment.objects.all()

    payment_data = [
        {
            "user": payment.user.username,
            "transaction_id": payment.transaction_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "created_at": payment.created_at,
        }
        for payment in payments
    ]

    return Response(payment_data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_subscriptions_overview(request):
    """Fetches all subscriptions for admin review"""
    subscriptions = Subscription.objects.all()

    subscription_data = [
        {
            "user": sub.user.username,
            "plan_name": sub.plan_name,
            "status": sub.status,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "auto_renewal": sub.auto_renewal,
        }
        for sub in subscriptions
    ]

    return Response(subscription_data)

@api_view(["POST"])
def payment_webhook(request):
    """Handles webhook notifications from payment providers"""
    provider = request.data.get("provider")
    transaction_id = request.data.get("transaction_id")
    payment_status = request.data.get("status")

    try:
        payment = Payment.objects.get(transaction_id=transaction_id)

        if payment_status == "success":
            payment.status = "successful"
            payment.booking.status = "approved"  # Approve booking upon successful payment
            payment.booking.save()
        else:
            payment.status = "failed"

        payment.save()
        return Response({"message": "Payment status updated", "provider": provider})

    except Payment.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)