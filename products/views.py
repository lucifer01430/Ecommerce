from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from products.models import Product, SizeVariant
from accounts.models import Cart, CartItems

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


# Cart view for logged-in user
def cart(request):
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    context = {'cart': cart}

    if request.method == 'POST':
        pass  # future logic

    return render(request, 'accounts/cart.html', context)


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
