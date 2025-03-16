from django.db import models
from company.models import Company
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now
from services.models import Service
from bookings.models import Booking
from django.contrib.auth import get_user_model


user = get_user_model()

class Currency(models.Model):
    """Stores supported currencies and exchange rates"""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    symbol = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.name} ({self.code})"

class CurrencyExchangeRate(models.Model):
    """Stores exchange rates for multi-currency support"""
    currency_code = models.CharField(max_length=10, unique=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)  # Relative to USD
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.currency_code} - {self.exchange_rate}"

class PaymentGateway(models.TextChoices):
    PAYSTACK = 'paystack', 'Paystack'
    FLUTTERWAVE = 'flutterwave', 'Flutterwave'

class Payment(models.Model):
    """Tracks payments for service bookings"""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_from_payments")
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    gateway = models.CharField(max_length=50)
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    def get_currency_symbol(self):
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "NGN": "₦",
            "JPY": "¥",
            "INR": "₹",
            "AUD": "A$",
            "CAD": "C$",
            "CHF": "CHF",
            "CNY": "¥",
        }
        return currency_symbols.get(self.currency, "$")

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} {self.amount} {self.currency} ({self.status})"

class RefundRequest(models.Model):
    """Stores refund requests for payments"""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund - {self.user.email} - {self.user.username} - {self.payment.transaction_id} ({self.status})"


    def approve(self):
        """Approve the refund and process it"""
        self.status = "approved"
        self.processed_at = now()
        self.save()
        # Process refund via the payment gateway (implementation later)

    def reject(self):
        """Reject the refund request"""
        self.status = "rejected"
        self.processed_at = now()
        self.save()

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

class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()

    def generate_invoice_number(self):
        """Create a unique invoice number"""
        return f"INV-{self.payment.id}-{int(self.issued_at.timestamp())}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
