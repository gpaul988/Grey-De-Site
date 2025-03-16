from django.core.mail import EmailMessage
from django.conf import settings

def send_service_completion_email(user, service):
    subject = f"Your {service.name} service is completed!"
    message = f"Hello {user.username},\n\nYour {service.name} service has been completed. We hope you are satisfied with the result.\n\nThank you for choosing Grey InfoTech!"
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.send()
