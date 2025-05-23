from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, SizeVariant

def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)

        cart_count = 0
        if request.user.is_authenticated:
            cart_count = CartItems.objects.filter(cart__is_paid=False, cart__user=request.user).count()

        context = {
            'product': product,
            'cart_count': cart_count,
        }

        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size
            context['updated_price'] = price

        return render(request, 'product/product.html', context=context)

    except Product.DoesNotExist:
        return redirect('/')
        
def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}

        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size
            context['updated_price'] = price

        return render(request, 'product/product.html', context=context)

    except Product.DoesNotExist:
        return redirect('/')

