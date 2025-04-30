from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
import datetime
from decimal import Decimal
from accounts.models import Cart
from .models import Order, OrderItem


@login_required(login_url='/accounts/login/')
def place_order(request):
    if request.method == 'POST':
        user = request.user
        cart = Cart.objects.filter(user=user, is_paid=False).first()

        if not cart or cart.cart_items.count() == 0:
            messages.warning(request, "Your cart is empty!")
            return redirect('cart')

        # Billing info
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        payment_method = request.POST.get('payment_method', 'COD')

        subtotal = sum(item.get_product_price() for item in cart.cart_items.all())
        discount = cart.coupon.discount_price if cart.coupon and subtotal >= cart.coupon.minimum_amount else Decimal('0.00')
        total_price = subtotal - discount

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

        for item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                size_variant=item.size_variant,
                color_variant=item.color_variant
            )

        cart.is_paid = True
        cart.save()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success')

    return redirect('checkout')


@login_required(login_url='/accounts/login/')
def order_success(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'orders/order_success.html', {'order': latest_order})


@login_required
def download_invoice(request, uid):
    order = get_object_or_404(Order, uid=uid, user=request.user)
    item_id = request.GET.get('item_id')
    item = None

    if item_id:
        try:
            item = order.order_items.get(id=item_id)
            order_items = [item]
        except OrderItem.DoesNotExist:
            return HttpResponse("Item not found in this order.", status=404)
    else:
        order_items = order.order_items.all()

    for i in order_items:
        i.unit_price = i.get_product_price() / i.quantity if i.quantity else Decimal("0.00")
        i.total_price = i.get_product_price()

    shipping_total = Decimal("50.00")
    total_amount = sum(i.total_price for i in order_items) + shipping_total

    context = {
        'order': order,
        'item': item,
        'order_items': order_items,
        'shipping_total': shipping_total,
        'total_amount': total_amount,
        'invoice_date': datetime.datetime.now().date(),
    }

    html_string = get_template("orders/invoice_template.html").render(context)
    html = HTML(string=html_string)
    pdf_file = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 20mm; }')])

    filename = f"Invoice_{order.short_order_id}"
    if item:
        filename += f"-P{item.id}"

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}.pdf'
    return response


@login_required
def preview_invoice(request, uid):
    order = get_object_or_404(Order, uid=uid, user=request.user)
    item_id = request.GET.get("item_id")
    item = None

    if item_id:
        try:
            item = order.order_items.get(id=item_id)
            order_items = [item]
        except OrderItem.DoesNotExist:
            return HttpResponse("Item not found.", status=404)
    else:
        order_items = order.order_items.all()

    for i in order_items:
        i.unit_price = i.get_product_price() / i.quantity if i.quantity else Decimal("0.00")
        i.total_price = i.get_product_price()

    shipping_total = Decimal("50.00")
    total_amount = sum(i.total_price for i in order_items) + shipping_total

    context = {
        'order': order,
        'item': item,
        'order_items': order_items,
        'shipping_total': shipping_total,
        'total_amount': total_amount,
        'invoice_date': datetime.datetime.now().date(),
    }

    return render(request, "orders/invoice_template.html", context)

