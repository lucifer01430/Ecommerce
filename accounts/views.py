from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Profile, Cart, CartItems
from products.models import Product, SizeVariant, Coupon
import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order 

# ------------------ Auth Views ------------------ #

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


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

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
            return redirect(next_url or '/')
        else:
            messages.warning(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


def activate_email(request, email_token):
    try:
        profile = Profile.objects.get(email_token=email_token)
        profile.is_email_verified = True
        profile.email_token = None
        profile.save()
        messages.success(request, "Email verified! You can now login.")
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired activation link.")
    return redirect('login')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# ------------------ Cart Views ------------------ #

def add_to_cart(request, uid):
    product = get_object_or_404(Product, uid=uid)
    variant = request.GET.get('variant')

    # Use user cart if authenticated, else session cart
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    else:
        if not request.session.session_key:
            request.session.save()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, is_paid=False)

    cart_item = CartItems.objects.create(cart=cart, product=product)

    if variant:
        size_variant = get_object_or_404(SizeVariant, size_name=variant)
        cart_item.size_variant = size_variant
        cart_item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print("Error removing cart item:", e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart(request):
    if request.user.is_authenticated:
        cart_obj = Cart.objects.filter(user=request.user, is_paid=False).first()
    else:
        cart_obj = Cart.objects.filter(session_key=request.session.session_key, is_paid=False).first()

    cart_items = cart_obj.cart_items.all() if cart_obj else []

    # Handle coupon removal
    if request.GET.get('remove_coupon') == 'true' and cart_obj:
        cart_obj.coupon = None
        cart_obj.save()
        messages.success(request, "Coupon removed successfully!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Handle coupon application
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__iexact=coupon_code, is_expired=False).first()

        if not coupon_obj:
            messages.warning(request, "Invalid coupon code!")
        elif cart_obj.coupon:
            messages.warning(request, "A coupon is already applied.")
        else:
            subtotal = sum([item.get_product_price() for item in cart_items])
            if subtotal < coupon_obj.minimum_amount:
                messages.warning(request, f"Coupon applicable on orders above ₹{coupon_obj.minimum_amount}.")
            else:
                cart_obj.coupon = coupon_obj
                cart_obj.save()
                messages.success(request, f"Coupon '{coupon_obj.coupon_code}' applied successfully!")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Price calculation
    subtotal = sum([item.get_product_price() for item in cart_items])
    discount = cart_obj.coupon.discount_price if cart_obj and cart_obj.coupon and subtotal >= cart_obj.coupon.minimum_amount else 0
    final_total = subtotal - discount

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
            except Exception as e:
                print("Quantity update error:", e)

    messages.success(request, "Cart quantities updated.")
    return redirect('cart')


def get_cart_count(request):
    cart = None

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    else:
        if not request.session.session_key:
            request.session.save()
        cart = Cart.objects.filter(session_key=request.session.session_key, is_paid=False).first()

    count = cart.cart_items.count() if cart else 0
    return JsonResponse({'count': count})

@login_required(login_url='/accounts/login/')
def checkout(request):
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    cart_items = cart.cart_items.all() if cart else []

    subtotal = sum([item.get_product_price() for item in cart_items])
    discount = cart.coupon.discount_price if cart and cart.coupon and subtotal >= cart.coupon.minimum_amount else 0
    total_price = subtotal - discount

    context = {
        'cart_items': cart_items,
        'cart': cart,
        'subtotal': subtotal,
        'discount': discount,
        'total_price': total_price,
        'user': request.user,
        'profile': request.user.profile
    }
    return render(request, 'accounts/checkout.html', context)

@csrf_exempt
@login_required(login_url='/accounts/login/')
def place_order(request):
    if request.method == 'POST':
        # For now, just show a success message (you can save order here)
        messages.success(request, "Your order has been placed successfully!")
        return redirect('home')  # ya 'order_success' later
    else:
        return redirect('checkout')

@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = request.user
    profile = user.profile

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)



@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = request.user
    profile = user.profile
    orders = Order.objects.filter(user=user).order_by('-created_at')  # ✅ All user's orders

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)

from orders.models import Order

@login_required
def dashboard_home(request):
    return render(request, 'accounts/dashboard/dashboard_home.html')

@login_required
def dashboard_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/dashboard/dashboard_orders.html', {'orders': orders})

@login_required
def dashboard_profile(request):
    return render(request, 'accounts/dashboard/dashboard_profile.html', {'user': request.user, 'profile': request.user.profile})

@login_required
def dashboard_coupons(request):
    return render(request, 'accounts/dashboard/dashboard_coupons.html')

@login_required
def dashboard_help(request):
    return render(request, 'accounts/dashboard/dashboard_help.html')
