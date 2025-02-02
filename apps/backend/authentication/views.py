from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer
from authentication.permissions import IsSuperAdmin, IsAdminOrSuperAdmin
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperAdmin, IsAdminOrSuperAdmin, IsSameCompany
from .models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Dynamically assign permissions based on request type."""
        if self.action in ['list', 'retrieve']:
            return [IsAdminOrSuperAdmin()]
        elif self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsSameCompany()]
        return super().get_permissions()

class CreateCompanyView(APIView):
    """
    View to create a company. Only accessible by Super Admin.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        """
        Handle POST request to create a company.
        """
        return Response({"message": "Company created successfully!"})

    class AdminOnlyView(APIView):
        """
        View accessible by Admin and Super Admin only.
        """
        permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

        def get(self, request):
            """
            Handle GET request for Admins.
            """
            return Response({"message": "Access granted for Admins"})

class LoginView(APIView):
    """
    View to handle user login.
    """
    def post(self, request):
        """
        Handle POST request for user login.
        """
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role
                },
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)