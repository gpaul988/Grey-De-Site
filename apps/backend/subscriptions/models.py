from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
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
    grace_period = models.IntegerField(default=7)  # Grace period in day


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