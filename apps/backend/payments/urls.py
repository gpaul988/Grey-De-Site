from django.urls import path
from .views import initiate_payment, payment_webhook

urlpatterns = [
    path("initiate/", initiate_payment, name="initiate_payment"),
    path("webhook/", payment_webhook, name="payment_webhook"),
]