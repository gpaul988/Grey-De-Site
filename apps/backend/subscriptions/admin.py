from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription
from django.utils.timezone import timedelta


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'grace_period')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'end_date')
    list_filter = ('status',)
    actions = ['cancel_subscription', 'extend_subscription']

    def cancel_subscription(self, request, queryset):
        """Cancels selected subscriptions"""
        queryset.update(status='expired')
        self.message_user(request, "Selected subscriptions have been cancelled.")

    def extend_subscription(self, request, queryset):
        """Extends subscription by 30 days"""
        for subscription in queryset:
            subscription.end_date += timedelta(days=30)
            subscription.save()
        self.message_user(request, "Selected subscriptions have been extended by 30 days.")
