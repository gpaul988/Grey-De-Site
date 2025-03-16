from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.mail import EmailMessage
from payments.choices import CURRENCY_CHOICES
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

user = get_user_model()

def send_service_completion_email(user, service):
    subject = f"Your {service.name} service is completed!"
    message = f"Hello {user.username},\n\nYour {service.name} service has been completed. We hope you are satisfied with the result.\n\nThank you for choosing Grey InfoTech!"
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.send()

class PaymentGateway(models.TextChoices):
    PAYSTACK = 'paystack', 'Paystack'
    FLUTTERWAVE = 'flutterwave', 'Flutterwave'

class Service(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("canceled", "Canceled"),
        ],
        default="pending",
    )
    description = models.TextField()
    progress = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("refunded", "Refunded"),
            ("pending", "Pending"),
        ],
        default="paid",
    )
    start_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)

    def update_progress(self, new_progress):
        """Update service progress and mark completion if 100%"""
        self.progress = new_progress
        if new_progress == 100:
            self.status = "completed"
            self.completion_date = now()
        self.save()

class ServiceBooking(models.Model):
    """Tracks service bookings and their progress"""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_bookings")
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    booked_on = models.DateTimeField(auto_now_add=True)
    expected_completion_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def mark_completed(self):
        """Mark a service as completed"""
        self.status = "completed"
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.service_name} ({self.status})"

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_from_services')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")
    gateway = models.CharField(max_length=20, choices=PaymentGateway.choices, default=PaymentGateway.PAYSTACK)
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    refunded_at = models.DateTimeField(null=True, blank=True)  # Store refund time

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} via {self.gateway} ({self.status})"

@receiver(post_save, sender=ServiceBooking)
def service_completed(sender, instance, created, **kwargs):
    """Automatically mark service as completed if certain conditions are met"""
    if sender == ServiceBooking and created and instance.status == "in_progress" and instance.completed_at:
        instance.status = "completed"
        instance.save()

        # Send a notification to the user about service completion
        send_service_completion_email(instance.user, instance.service)

        # Handle additional arguments if needed
        additional_info = kwargs.get('additional_info', None)
        if additional_info:
            # Process additional_info if provided
            pass

class UploadedFile(models.Model):
    """Stores files uploaded by clients for LLM analysis"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"