from django.core.mail import send_mail
from django.conf import settings

def send_account_activation_email(email, email_token):
    subject = 'Activate Your Account - YourSite'
    email_from = settings.EMAIL_HOST_USER
    activation_link = f'http://127.0.0.1:8000/accounts/activate/{email_token}/'

    html_message = f"""
    <div style="max-width: 600px; margin: auto; font-family: Arial, sans-serif; text-align: center; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <img src="https://cdn-icons-png.flaticon.com/128/397/397181.png" alt="YourSite Logo" style="width: 80px; margin-bottom: 20px;">
        <h2 style="color: #333;">Welcome to YourSite!</h2>
        <p style="color: #555;">Click the button below to verify your email and activate your account.</p>
        <a href="{activation_link}" style="display: inline-block; background: #007bff; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; margin-top: 15px;">Verify Email</a>
        <p style="margin-top: 20px; color: #777;">If you didn’t sign up, you can safely ignore this email.</p>
        <hr style="margin: 20px 0;">
        <p style="color: #999; font-size: 12px;">YourSite &copy; 2025. All Rights Reserved.</p>
    </div>
    """

    return send_mail(subject, '', email_from, [email], fail_silently=False, html_message=html_message)
