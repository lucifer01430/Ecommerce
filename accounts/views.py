from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Profile
import uuid
from django.core.mail import send_mail
from django.conf import settings


def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.warning(request, "Email already registered!")
            return HttpResponseRedirect(request.path_info)

        # Create user
        user_obj = User.objects.create_user(username=email, email=email, password=password)
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.save()

        # Check if Profile already exists
        if not Profile.objects.filter(user=user_obj).exists():
            profile_obj = Profile.objects.create(user=user_obj, email_token=str(uuid.uuid4()))
            profile_obj.save()
        
        messages.success(request, "Account created successfully! Verify your email to login.")
        return redirect('/accounts/login/')  # Redirect to login after successful registration

    return render(request, 'accounts/register.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=email).first()

        if not user_obj:
            messages.warning(request, "Account does not exist!")
            return HttpResponseRedirect(request.path_info)

        if not getattr(user_obj, 'profile', None) or not user_obj.profile.is_email_verified:
            messages.warning(request, "Account not verified!")
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(request, username=user_obj.username, password=password)

        if user_obj is not None:
            login(request, user_obj)
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, "Invalid credentials")
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')

def activate_email(request, email_token):
    try:
        profile = Profile.objects.get(email_token=email_token)
        profile.is_email_verified = True
        profile.email_token = None
        profile.save()
        messages.success(request, "Email verified successfully! You can now login.")
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "Invalid Email Token")
        return redirect('register')
