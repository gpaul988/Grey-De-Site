from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.backend.middleware.subscription_middleware import subscription_required

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@subscription_required("premium")
def analyze_uploaded_file(request):
    """LLM AI service that analyzes uploaded files"""
    # AI processing logic here
    return Response({"message": "AI processing complete!"})