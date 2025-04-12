from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Cart, CartItems
from products.models import Product, SizeVariant, Coupon
import uuid
from django.views.decorators.http import require_POST


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


# Logout View
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# Add-to-cart View
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


# Remove-from-cart View
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

    cart_obj = Cart.objects.filter(user=request.user, is_paid=False).first()
    cart_items = cart_obj.cart_items.all() if cart_obj else []

    # Remove coupon if requested
    if request.GET.get('remove_coupon') == 'true' and cart_obj:
        cart_obj.coupon = None
        cart_obj.save()
        messages.success(request, "Coupon removed successfully!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Apply coupon logic
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__iexact=coupon_code, is_expired=False).first()

        if not coupon_obj:
            messages.warning(request, "Invalid coupon code!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_obj.coupon:
            messages.warning(request, "A coupon is already applied.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        subtotal = sum([item.get_product_price() for item in cart_items])
        if subtotal < coupon_obj.minimum_amount:
            messages.warning(request, f"Coupon '{coupon_obj.coupon_code}' applicable on orders above ₹{coupon_obj.minimum_amount}.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart_obj.coupon = coupon_obj
        cart_obj.save()
        messages.success(request, f"Coupon '{coupon_obj.coupon_code}' applied successfully!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Pricing calculation
    subtotal = sum([item.get_product_price() for item in cart_items])
    discount = 0
    if cart_obj and cart_obj.coupon:
        if subtotal >= cart_obj.coupon.minimum_amount:
            discount = cart_obj.coupon.discount_price
    final_total = subtotal - discount

    # All active coupons for suggestion
    active_coupons = Coupon.objects.filter(is_expired=False)

    context = {
        'cart': cart_obj,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total_price': final_total,
        'available_coupons': active_coupons,
    }
    return render(request, 'accounts/cart.html', context)

@require_POST
def update_cart_quantities(request):
    for key, value in request.POST.items():
        if key.startswith('quantity_'):
            try:
                cart_item_id = key.split('quantity_')[1]
                cart_item = CartItems.objects.get(uid=cart_item_id)
                quantity = int(value)
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
            except:
                pass  # Handle errors silently for now

    messages.success(request, "Cart quantities updated.")
    return redirect('cart')