from django.core.mail import send_mail
from django.conf import settings

def send_account_activation_email(email, email_token):
    subject = 'Activate your account'
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi, Click on the link to activate your account:\n\nhttp://127.0.0.1:8000/accounts/activate/{email_token}'
    
    return send_mail(subject, message, email_from, [email], fail_silently=False)
