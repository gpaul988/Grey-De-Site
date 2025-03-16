import requests
from .models import PaymentGateway
from django.conf import settings

def process_payment_refund(service):
    """
    Process the refund for the given service.
    Integrate with the actual payment gateway.
    """
    payment = service.payment

    if payment.gateway == PaymentGateway.PAYSTACK:
        return process_paystack_refund(payment)
    elif payment.gateway == PaymentGateway.FLUTTERWAVE:
        return process_flutterwave_refund(payment)
    else:
        # Handle other gateways or raise an error
        return False

def process_paystack_refund(payment):
    """Process refund via Paystack"""
    url = f"https://api.paystack.co/refund"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "transaction": payment.reference,
        "amount": int(payment.amount * 100)  # Amount in kobo
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

def process_flutterwave_refund(payment):
    """Process refund via Flutterwave"""
    url = f"https://api.flutterwave.com/v3/refunds"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "transaction_id": payment.reference,
        "amount": payment.amount
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200