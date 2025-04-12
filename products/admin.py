from django.contrib import admin

# Register your models here.
from .models import Category, Product, ProductImage, ColorVariant, SizeVariant , Coupon

# Register Category model
admin.site.register(Category)
admin.site.register(Coupon)  # Assuming Coupon is defined in models.py

# Inline model for product images
class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

# Admin model for Product with inline images
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'price', 'product_description']
    inlines = [ProductImageAdmin]

# Registering ProductAdmin with the Product model
admin.site.register(Product, ProductAdmin)

# Registering ProductImage directly
admin.site.register(ProductImage)

# Admin model for ColorVariant
@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']

# Admin model for SizeVariant
@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price']
