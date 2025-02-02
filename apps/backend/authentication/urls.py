
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, UserViewSet
from .file_uploads_views import FileUploadView

router = DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('upload-profile-picture/', FileUploadView.as_view(), name='upload-profile-picture'),
    path('', include(router.urls)),
]