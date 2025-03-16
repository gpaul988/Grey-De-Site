from rest_framework import serializers
from .models import Invoice, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Invoice
        fields = '__all__'