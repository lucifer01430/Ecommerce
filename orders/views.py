from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Cart, CartItems
from .models import Order, OrderItem
from django.contrib import messages

@login_required(login_url='/accounts/login/')
def place_order(request):
    if request.method == 'POST':
        user = request.user
        cart = Cart.objects.filter(user=user, is_paid=False).first()

        if not cart or cart.cart_items.count() == 0:
            messages.warning(request, "Your cart is empty!")
            return redirect('cart')

        # Collect billing information from checkout form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        payment_method = request.POST.get('payment_method', 'COD')

        subtotal = sum([item.get_product_price() for item in cart.cart_items.all()])
        discount = cart.coupon.discount_price if cart.coupon and subtotal >= cart.coupon.minimum_amount else 0
        total_price = subtotal - discount

        # Create the Order
        order = Order.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            payment_method=payment_method,
            total_amount=total_price,
            status='Placed'
        )

        # Create Order Items
        for item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                size_variant=item.size_variant,
                color_variant=item.color_variant
            )

        # Mark cart as paid
        cart.is_paid = True
        cart.save()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success')  # we'll create this page next
    else:
        return redirect('checkout')

from django.shortcuts import render

@login_required(login_url='/accounts/login/')
def order_success(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    context = {
        'order': latest_order,
    }
    return render(request, 'orders/order_success.html', context)
