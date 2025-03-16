from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from payments.views import get_currencies
from bookings.views import create_booking, update_booking_status, get_user_bookings

def home(_request):
    return HttpResponse("Welcome to the homepage!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('invoices/', include('invoices.urls')),
    path('media/<path:path>/', include('media.urls')),
    path('', home),  # Add this line to handle the root URL
    path("currencies/", get_currencies, name="get_currencies"),
    path("book/", create_booking, name="create_booking"),
    path("update/<int:booking_id>/", update_booking_status, name="update_booking_status"),
    path("my-bookings/", get_user_bookings, name="get_user_bookings"),
]