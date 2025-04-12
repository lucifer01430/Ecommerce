from django.urls import path
from accounts.views import (
    login_page, register_page, activate_email, cart, add_to_cart,
    remove_cart, update_cart_quantities  # ✅ added here
)

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('activate/<str:email_token>/', activate_email, name='activate_email'),
    path('cart/', cart, name='cart'),
    path('add_to_cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('remove_cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
    path('update_cart_quantities/', update_cart_quantities, name='update_cart_quantities'),  # ✅ added here
]
