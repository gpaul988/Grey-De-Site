import requests
from django.db import models
from datetime import datetime
from django.conf import settings
from payments.models import Payment
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta


User = get_user_model()

class SubscriptionPlan(models.Model):
    """Subscription plans available for users."""
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=200, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in local currency
    duration = models.IntegerField()  # E.g., 30 for monthly plan
    features = models.TextField()  # List of features included in the plan
    grace_period = models.IntegerField(default=7)  # Grace period in days
    currency = models.CharField(max_length=10, default='USD')  # Currency for the plan


    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    """Tracks which users are subscribed to which plans."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('grace', 'Grace Period')
    ], default='active')
    auto_renew = models.BooleanField(default=True)  # Enable auto-renewal

    def is_active(self):
        """Check if subscription is still valid"""
        return self.end_date >= datetime.now()

    def extend_subscription(self):
        """Extend subscription based on the plan duration"""
        self.end_date += timedelta(days=self.plan.duration)
        self.save()

    def is_within_grace_period(self):
        """Checks if subscription is still within grace period"""
        return self.end_date < now() < (self.end_date + timedelta(days=self.plan.grace_period))

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("grace_period", "Grace Period"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.OneToOneField(SubscriptionPlan, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    grace_period_end = models.DateTimeField(null=True, blank=True)
    auto_renewal = models.BooleanField(default=True)  # Enables auto-renewal

    @property
    def plan_name(self):
        return self.plan.name

    def save(self, *args, **kwargs):
        """Automatically set grace period end when subscription expires"""
        if self.status == "expired" and not self.grace_period_end:
            self.grace_period_end = self.end_date + timedelta(days=5)  # 5-day grace period
            self.status = "grace"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.plan_name} ({self.status})"

    def check_status(self):
        """Auto-update status based on end date"""
        if self.status in ["canceled", "expired"]:
            return

        if now() >= self.end_date:
            if self.auto_renewal:
                self.renew_subscription()
            else:
                self.status = "grace_period"
                self.grace_period_end = self.end_date + timedelta(days=7)  # 7-day grace period
                self.save()

        if self.status == "grace_period" and now() >= self.grace_period_end:
            self.status = "expired"
            self.save()

    def renew_subscription(self):
        """Automatically renew the subscription if enabled"""
        if self.auto_renewal:
            self.end_date += timedelta(days=self.plan.duration)
            self.save()

    @staticmethod
    def process_payment(payment):
        """Process the payment using the selected gateway"""
        if payment.gateway == "paystack":
            response = requests.post(
                f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
                headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
                json={
                    "email": payment.user.email,
                    "amount": int(payment.amount * 100),  # Convert to kobo
                    "currency": payment.currency,
                    "reference": payment.reference,
                },
            )
        elif payment.gateway == "flutterwave":
            response = requests.post(
                f"{settings.FLUTTERWAVE_BASE_URL}/payments",
                headers={"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"},
                json={
                    "tx_ref": payment.reference,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "redirect_url": "https://your-redirect-url.com",
                    "customer": {
                        "email": payment.user.email,
                    },
                },
            )
        else:
            raise ValueError("Unsupported payment gateway")

        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            payment.status = "successful"
        else:
            payment.status = "failed"
        payment.save()
        return payment.status == "successful"

    def is_active(self):
        return self.end_date >= datetime.now()

    def enter_grace_period(self):
        """Extend grace period by 7 days after expiration"""
        self.grace_period_end = self.end_date + timedelta(days=7)
        self.save()

    def extend_subscription(self):
        """Extend subscription based on the plan duration"""
        self.end_date += timedelta(days=self.plan.duration)
        self.save()

    def send_expiry_notification(self):
        """Send email notification to user about subscription expiry"""
        send_mail(
            subject="Subscription Expiry Notice",
            message=f"Hello {self.user.username}, your subscription is expiring soon. Renew now to avoid interruption.",
            from_email="support@greyinfotech.com",
            recipient_list=[self.user.email],
        )