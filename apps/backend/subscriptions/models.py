from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from payments.models import Payment
from django.conf import settings

class SubscriptionPlan(models.Model):
    """Subscription plans available for users."""
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=200, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in local currency
    duration = models.IntegerField(help_text="Duration in days")  # E.g., 30 for monthly plan
    grace_period = models.IntegerField(default=7)  # Grace period in days
    currency = models.CharField(max_length=10, default='USD')  # Currency for the plan


    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    """Tracks which users are subscribed to which plans."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('grace', 'Grace Period')
    ], default='active')

    def is_active(self):
        """Check if subscription is still valid"""
        from django.utils.timezone import now
        return self.end_date > now()

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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    grace_period_end = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)  # Enables auto-renewal

    def check_status(self):
        """Auto-update status based on end date"""
        if self.status in ["canceled", "expired"]:
            return

        if now() >= self.end_date:
            if self.auto_renew:
                self.renew_subscription()
            else:
                self.status = "grace_period"
                self.grace_period_end = self.end_date + timedelta(days=7)  # 7-day grace period
                self.save()

        if self.status == "grace_period" and now() >= self.grace_period_end:
            self.status = "expired"
            self.save()

    def renew_subscription(self):
        """Automatically renew subscription if payment succeeds"""
        new_payment = Payment.objects.create(
            user=self.user,
            amount=self.plan.price,
            currency=self.plan.currency,
            gateway=self.payment.gateway,
            reference=f"{self.user.id}-{now().timestamp()}",
            status="pending"
        )

        # Simulate a payment gateway response
        payment_success = self.process_payment(new_payment)

        if payment_success:
            self.status = "active"
            self.start_date = now()
            self.end_date = now() + timedelta(days=self.plan.duration)
            self.payment = new_payment
            self.save()
        else:
            self.status = "grace_period"
            self.grace_period_end = self.end_date + timedelta(days=7)
            self.save()

    def process_payment(self, payment):
        """Process the payment using the selected gateway (Mock)"""
        # TODO: Integrate actual payment gateway processing here
        payment.status = "successful"
        payment.save()
        return True