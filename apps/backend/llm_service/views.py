import openai
import pdfplumber
import pytesseract
import cv2
import os
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# OpenAI API Key
openai.api_key = settings.OPENAI_API_KEY

# Supported services
SERVICES = [
    "Web Design", "Web App Development", "Web Development", "Wix Development", "WordPress Development",
    "AI Development", "Android Development", "Blockchain Development", "Cross Platform Development",
    "Flutter Development", "iOS Development", "Vue.js Development", "Squarespace Development", "Shopify Development",
    "React Development", "PHP Development", "Next.js Development", "Node.js Development", "Laravel Development",
    "Drupal Development", "Joomla Development", "CMS Development", "Angular Development", "Python Development",
    "Django Development", "Ruby on Rails Development", "Mac Software Development", "React Native Development",
    "Software Development", "Windows Software Development", "App Store Optimization", "SEO", "Social Media Marketing",
    "Ecommerce Development"
]


def extract_text_from_file(file_path):
    """Extract text from PDFs, images, or videos."""
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    elif file_ext in [".jpg", ".png"]:
        return pytesseract.image_to_string(file_path)


    elif file_ext in [".mp4", ".avi"]:
        cap = cv2.VideoCapture(file_path)
        text = ""
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text += pytesseract.image_to_string(gray)
        cap.release()
        return text if text else "No text found in video."

    else:
        return None


@api_view(["POST"])
@permission_classes([AllowAny])
def analyze_uploaded_file(request):
    """Processes user-uploaded files and recommends a service."""
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response({"error": "No file uploaded."}, status=400)

    file_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)

    extracted_text = extract_text_from_file(file_path)

    if not extracted_text:
        return Response({"error": "Could not extract text from file."}, status=400)

    # LLM Prompt
    prompt = f"""
    A client uploaded a file containing the following text:

    {extracted_text}

    Based on this, recommend the most suitable service from Grey Infotech.
    Only provide the service name and an estimated time to complete it.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    recommendation = response["choices"][0]["message"]["content"]

    return Response({"recommendation": recommendation})
