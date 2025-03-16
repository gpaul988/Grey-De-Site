from django.db import models
from django.conf import settings
from services.models import Service

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/')
    address = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return self.name

class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField('payments.Payment', on_delete=models.CASCADE, related_name='invoice_payment')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='invoice_services')
    invoice_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_invoices')

    def generate_invoice_number(self):
        """Create a unique invoice number"""
        return f"INV-{self.payment.id}-{int(self.issued_at.timestamp())}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.user}"