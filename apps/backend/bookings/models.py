from django.db import models
from django.contrib.auth import get_user_model
from services.models import Service

User = get_user_model()

class Booking(models.Model):
    """Model for service bookings"""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.ForeignKey('payments.Currency', on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    auto_renewal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.status})"