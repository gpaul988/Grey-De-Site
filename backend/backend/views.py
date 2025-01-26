import logging
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def home(request):
    return HttpResponse("Welcome to the home page!")

def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            email = data.get('email', '')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({'message': 'User registered successfully'}, status=201)
        except Exception as e:
            logger.error(f"Error during user registration: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)