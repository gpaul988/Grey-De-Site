from rest_framework import serializers
from .models import Subscription, Payment, PaymentGateway

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'currency', 'gateway', 'reference', 'status', 'created_at', 'updated_at', 'refunded_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_currency(self, value):
        valid_currencies = ['USD', 'NGN', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR']
        if value not in valid_currencies:
            raise serializers.ValidationError(f"Currency must be one of {valid_currencies}.")
        return value

    def validate_gateway(self, value):
        valid_gateways = [choice[0] for choice in PaymentGateway.choices()]
        if value not in valid_gateways:
            raise serializers.ValidationError(f"Gateway must be one of {valid_gateways}.")
        return value