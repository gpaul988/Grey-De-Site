from django.db import models
from django.conf import settings
from django.utils.timezone import now
from payments.models import CURRENCY_CHOICES
from django.utils.translation import gettext_lazy as _

class PaymentGateway(models.TextChoices):
    PAYSTACK = 'paystack', 'Paystack'
    FLUTTERWAVE = 'flutterwave', 'Flutterwave'

class ServiceBooking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")
        CANCELED = "canceled", _("Canceled")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey("payments.Payment", on_delete=models.CASCADE, null=True, blank=True)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    scheduled_date = models.DateTimeField()

    def confirm_booking(self):
        """Confirm booking after successful payment"""
        if self.payment and self.payment.status == "successful":
            self.status = "confirmed"
            self.save()

    def __str__(self):
        return f"{self.user} - {self.service} ({self.status})"

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")
    gateway = models.CharField(max_length=20, choices=PaymentGateway.choices, default=PaymentGateway.PAYSTACK)
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    refunded_at = models.DateTimeField(null=True, blank=True)  # Store refund time

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} via {self.gateway} ({self.status})"