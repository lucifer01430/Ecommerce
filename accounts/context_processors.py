from .models import Cart

def cart_count_processor(request):
    cart = None

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    else:
        if not request.session.session_key:
            request.session.save()
        cart = Cart.objects.filter(session_key=request.session.session_key, is_paid=False).first()

    count = cart.cart_items.count() if cart else 0
    return {'cart_count': count}
