import requests
from django.conf import settings
from .models import Currency


def fetch_exchange_rates():
    """Fetch real-time exchange rates from an API"""
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"https://open.er-api.com/v6/latest/USD?apikey={api_key}"

    response = requests.get(url)
    data = response.json()

    if "rates" in data:
        for code, rate in data["rates"].items():
            Currency.objects.update_or_create(code=code, defaults={"exchange_rate": rate})
        return "Exchange rates updated"

    return "Failed to fetch exchange rates"
