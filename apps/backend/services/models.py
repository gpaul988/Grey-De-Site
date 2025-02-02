from django.db import models
from django.contrib.auth.models import User
from payments.models import CURRENCY_CHOICES
from django.conf import settings


class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey("payments.Payment", on_delete=models.CASCADE, null=True, blank=True)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")
    status = models.CharField(max_length=20,
                              choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("completed", "Completed"),
                                       ("canceled", "Canceled")], default="pending")
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
