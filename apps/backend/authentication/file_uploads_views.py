from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')
        if file is None:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Save file to MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Call LLM API for service recommendation (this is a mock for now)
        recommended_service = self.process_file(file_path)

        return Response({
            "message": "File uploaded successfully",
            "recommended_service": recommended_service
        })

    def process_file(self, file_path):
        # Placeholder function for LLM integration
        # In reality, you'd process the file and return a service recommendation
        if file_path.endswith('.pdf') or file_path.endswith('.doc') or file_path.endswith('.docx'):
            return "Document Review & Editing"
        elif file_path.endswith('.jpg') or file_path.endswith('.png'):
            return "Graphic Design & Branding"
        elif file_path.endswith('.mp4') or file_path.endswith('.mkv'):
            return "Video Editing"
        elif file_path.endswith('.mp3') or file_path.endswith('.wav'):
            return "Audio Editing"
        elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            return "Data Analysis & Reporting"
        else:
            return "General Consultation"