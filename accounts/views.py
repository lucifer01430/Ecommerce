from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Profile
import uuid


# User Registration View
def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.warning(request, "Email already registered!")
            return redirect('register')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        # Profile will be auto-created via post_save signal

        messages.success(request, "Account created successfully! Please verify your email before logging in.")
        return redirect('login')

    return render(request, 'accounts/register.html')


# User Login View
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(username=email).first()

        if not user:
            messages.warning(request, "Account does not exist!")
            return redirect('login')

        if not hasattr(user, 'profile') or not user.profile.is_email_verified:
            messages.warning(request, "Please verify your email before logging in.")
            return redirect('login')

        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return redirect('/')
        else:
            messages.warning(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


# Email Activation View
def activate_email(request, email_token):
    try:
        profile = Profile.objects.get(email_token=email_token)
        profile.is_email_verified = True
        profile.email_token = None
        profile.save()
        messages.success(request, "Email verified! You can now login.")
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired activation link.")
        return redirect('register')


# Logout View (recommended to add)
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')
