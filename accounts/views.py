from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Profile
import uuid

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Get user object using email as username
        user_obj = User.objects.filter(username=email).first()  # Use `.first()` to avoid index errors

        if not user_obj:
            messages.warning(request, "Account does not exist!")
            return HttpResponseRedirect(request.path_info)

        # Check if the user's email is verified
        if not getattr(user_obj, 'profile', None) or not user_obj.profile.is_email_verified:
            messages.warning(request, "Account not verified!")
            return HttpResponseRedirect(request.path_info)

        # Authenticate user
        user_obj = authenticate(request, username=user_obj.username, password=password)

        if user_obj is not None:
            login(request, user_obj)
            return HttpResponseRedirect('/')  # Redirect to home page
        else:
            messages.warning(request, "Invalid credentials")
            return HttpResponseRedirect(request.path_info)  # Redirect back to login page

    return render(request, 'accounts/login.html')

def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.warning(request, "Email already exists")
            return HttpResponseRedirect(request.path_info)

        # Create user
        user_obj = User.objects.create(username=email, first_name=first_name, last_name=last_name, email=email)
        user_obj.set_password(password)
        user_obj.save()

        # Create profile for email verification
        email_token = str(uuid.uuid4())  # Generate unique token
        profile, created = Profile.objects.get_or_create(user=user_obj)
        profile.email_token = email_token
        profile.save()

        # Optionally send email here

        messages.success(request, "A verification mail has been sent to your email address.")
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')

def activate_email(request, email_token):
    try:
        profile = Profile.objects.get(email_token=email_token)
        profile.is_email_verified = True
        profile.save()
        return redirect('/')
    except Profile.DoesNotExist:
        return HttpResponse('Invalid Email token')
