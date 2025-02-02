from rest_framework import viewsets, permissions
from .models import Company
from .serializers import CompanySerializer
from authentication.permissions import IsSuperAdmin, IsAdminOrSuperAdmin


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]  # Only Super Admin can create or delete companies

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAdminOrSuperAdmin]  # Admins can view companies
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
