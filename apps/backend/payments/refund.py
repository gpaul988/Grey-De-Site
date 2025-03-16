import requests
from django.conf import settings


def process_payment_refund(service):
    """Handles refund processing via multiple payment gateways"""

    # Check payment provider used
    provider = service.payment_provider

    if provider == "paystack":
        return refund_paystack(service)
    elif provider == "flutterwave":
        return refund_flutterwave(service)
    else:
        return False


def refund_paystack(service):
    """Refund logic for Paystack"""
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    data = {"transaction": service.transaction_id}

    response = requests.post("https://api.paystack.co/refund", headers=headers, json=data)
    return response.status_code == 200


def refund_flutterwave(service):
    """Refund logic for Flutterwave"""
    headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
    data = {"transaction_id": service.transaction_id}

    response = requests.post("https://api.flutterwave.com/v3/refunds", headers=headers, json=data)
    return response.status_code == 200
