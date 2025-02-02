from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role',)
    search_fields = ('email','first_name', 'last_name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)