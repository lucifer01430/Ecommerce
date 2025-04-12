from django.contrib import admin
from .models import Profile, Cart, CartItems

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_email_verified', 'email_token']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid', 'coupon', 'created_at']
    list_filter = ['is_paid']
    search_fields = ['user__username', 'coupon__coupon_code']

@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'color_variant', 'size_variant', 'created_at']
    search_fields = ['product__product_name', 'cart__user__username']
    list_filter = ['color_variant', 'size_variant']
