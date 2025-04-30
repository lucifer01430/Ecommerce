from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('activate/<str:email_token>/', views.activate_email, name='activate_email'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<uid>/', views.add_to_cart, name='add_to_cart'),
    path('remove_cart/<cart_item_uid>/', views.remove_cart, name='remove_cart'),
    path('update_cart_quantities/', views.update_cart_quantities, name='update_cart_quantities'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('logout/', views.logout_user, name='logout') ,
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    path('dashboard/coupons/', views.dashboard_coupons, name='dashboard_coupons'),
    path('dashboard/help/', views.dashboard_help, name='dashboard_help'),
]