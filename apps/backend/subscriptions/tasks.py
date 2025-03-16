import requests
from celery import shared_task
from datetime import timedelta
from django.conf import settings
from .models import Subscription
from payments.models import Payment
from bookings.models import Booking
from django.utils.timezone import now
from django.core.mail import send_mail
from .models import UserSubscription


@shared_task
def auto_renew_subscriptions():
    """Check for expired subscriptions and auto-renew if possible."""
    expired_subscriptions = UserSubscription.objects.filter(end_date__lt=now(), status='active')

    for subscription in expired_subscriptions:
        user = subscription.user
        plan = subscription.plan

        if subscription.is_within_grace_period():
            subscription.status = 'grace'
            subscription.save()
            print(f"Subscription for {user.email} is in grace period.")
            continue

        reference = f"renew_{user.id}_{now().timestamp()}"

        # Call payment gateway for auto-renewal
        response = requests.post(
            f"{settings.PAYSTACK_BASE_URL}/transaction/charge_authorization",
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            json={
                "email": user.email,
                "amount": int(plan.price * 100),  # Convert to kobo
                "authorization_code": user.profile.paystack_auth_code,  # Stored after first payment
                "reference": reference,
            },
        )

        data = response.json()
        if response.status_code == 200 and data["status"] == "success":
            # Extend subscription
            new_end_date = now() + timedelta(days=plan.duration)
            subscription.end_date = new_end_date
            subscription.status = 'active'
            subscription.save()
            print(f"Subscription renewed for {user.email}")
        else:
            subscription.status = 'expired'
            subscription.save()
            print(f"Failed to renew subscription for {user.email}. Subscription expired.")

def send_renewal_reminders():
    """Send email reminders for expiring subscriptions"""
    upcoming_subscriptions = UserSubscription.objects.filter(end_date__lt=now() + timedelta(days=3))

    for subscription in upcoming_subscriptions:
        user_email = subscription.user.email
        send_mail(
            "Subscription Renewal Reminder",
            f"Dear {subscription.user.username}, your {subscription.plan.name} plan expires soon. "
            "Ensure your payment method is up to date for auto-renewal.",
            "your_email@gmail.com",
            [user_email],
        )

def send_subscription_report():
    """Generates and sends a weekly subscription report to admins."""
    active_subs = UserSubscription.objects.filter(status="active").count()
    expiring_subs = UserSubscription.objects.filter(end_date__lte=now() + timedelta(days=7)).count()
    new_subs = UserSubscription.objects.filter(start_date__gte=now() - timedelta(days=7)).count()

    report = f"""
    📊 **Subscription Report**
    ----------------------------
    ✅ Active Subscriptions: {active_subs}
    ⏳ Expiring Soon: {expiring_subs}
    🆕 New Subscriptions (last 7 days): {new_subs}
    """

    send_mail(
        subject="Weekly Subscription Report",
        message=report,
        from_email="admin@greyinfotech.com",
        recipient_list=["admin@greyinfotech.com"],
    )

    return "Report sent!"

def send_renewal_reminder():
    """Sends renewal reminder emails to users whose subscriptions expire soon."""
    expiring_users = UserSubscription.objects.filter(end_date__lte=now() + timedelta(days=3), status="active")

    for sub in expiring_users:
        send_mail(
            subject="Your Subscription is Expiring Soon!",
            message=f"Hello {sub.user.email},\n\nYour subscription for {sub.plan.name} will expire in 3 days. Renew now to avoid service interruption.",
            from_email="support@greyinfotech.com",
            recipient_list=[sub.user.email],
        )

    return f"Sent reminders to {expiring_users.count()} users."

def check_all_subscriptions():
    """Runs daily to update subscription statuses"""
    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        subscription.check_status()

        # Check for monthly renewals
        if subscription.plan.duration == 30:
            subscription.check_status()

        # Check for yearly renewals
        elif subscription.plan.duration == 365:
            subscription.check_status()

def check_monthly_subscriptions():
    """Runs monthly to update subscription statuses"""
    monthly_subscriptions = Subscription.objects.filter(plan__duration=30)
    for subscription in monthly_subscriptions:
        subscription.check_status()

def check_yearly_subscriptions():
    """Runs yearly to update subscription statuses"""
    yearly_subscriptions = Subscription.objects.filter(plan__duration=365)
    for subscription in yearly_subscriptions:
        subscription.check_status()

def check_and_renew_subscriptions():
    """Check expired subscriptions and renew if auto-renew is enabled"""
    subscriptions = Subscription.objects.filter(end_date__lte=now())

    for sub in subscriptions:
        if sub.auto_renew:
            sub.renew_subscription()
        else:
            sub.enter_grace_period()


def notify_users_about_expiry():
    """Notify users whose subscriptions are expiring soon"""
    subscriptions = Subscription.objects.filter(end_date__lte=now() + timedelta(days=3))

    for sub in subscriptions:
        sub.send_expiry_notification()


@shared_task
def process_auto_renewals():
    """Checks for auto-renewal and processes payments"""
    bookings = Booking.objects.filter(auto_renewal=True, status="completed")

    for booking in bookings:
        user = booking.user
        transaction_id = f"auto_{user.id}_{booking.id}_{now().timestamp()}"

        # Create new payment entry
        payment = Payment.objects.create(
            user=user, booking=booking, provider=booking.payment.provider,
            transaction_id=transaction_id, amount=booking.total_price,
            currency=booking.currency.code, status="pending"
        )

        # Simulate successful renewal
        payment.status = "successful"
        payment.save()
        booking.status = "approved"
        booking.save()

    return f"Processed {bookings.count()} auto-renewals"

@shared_task
def check_subscription_status():
    """Updates expired subscriptions and handles grace period"""
    subscriptions = Subscription.objects.filter(status="active", end_date__lte=now())

    for sub in subscriptions:
        sub.status = "expired"
        sub.save()

    grace_subscriptions = Subscription.objects.filter(status="grace", grace_period_end__lte=now())

    for sub in grace_subscriptions:
        sub.status = "cancelled"
        sub.save()

    return f"Updated {subscriptions.count()} expired, {grace_subscriptions.count()} cancelled subscriptions."