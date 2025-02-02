from django.db import models
from company.models import Company
from django.contrib.auth.models import User
from django.conf import settings

CURRENCY_CHOICES = [
    ("NGN", "Nigerian Naira"),
    ("USD", "US Dollar"),
    ("GHS", "Ghanaian Cedi"),
    ("ZAR", "South African Rand"),
    ("EUR", "Euro"),
    ("GBP", "British Pound Sterling"),
    ("INR", "Indian Rupee"),
    ("JPY", "Japanese Yen"),
    ("CAD", "Canadian Dollar"),
]

PAYMENT_GATEWAY_CHOICES = [
    ("paystack", "Paystack"),
    ("flutterwave", "Flutterwave"),
]

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")
    gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAY_CHOICES, default="paystack")
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    refunded_at = models.DateTimeField(null=True, blank=True)  # Store refund time

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} via {self.gateway} ({self.status})"

class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund {self.status} - {self.payment.reference}"

class Subscription(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=[
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise')
    ])
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return f"{self.company.name} - {self.plan}"
