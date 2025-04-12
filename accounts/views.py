from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Profile
import uuid
from products.models import *
from accounts.models import Cart, CartItems


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


# Add-to-cart view
def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    product = get_object_or_404(Product, uid=uid)
    user = request.user

    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

    cart_item = CartItems.objects.create(cart=cart, product=product)

    if variant:
        size_variant = get_object_or_404(SizeVariant, size_name=variant)
        cart_item.size_variant = size_variant
        cart_item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

from django.http import HttpResponseRedirect

def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    cart_items = cart.cart_items.all() if cart else []

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_cart_total() if cart else 0
    }
    return render(request, 'accounts/cart.html', context)





