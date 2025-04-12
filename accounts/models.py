from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from products.models import Coupon, Product, ColorVariant, SizeVariant

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile', null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def cart_count(self):
        from accounts.models import CartItems  # To avoid circular import if needed
        return CartItems.objects.filter(cart__is_paid=False, cart__user=self.user).count()

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart of {self.user.username} | Paid: {self.is_paid}"

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        for cart_item in cart_items:
            if cart_item.product:
                price.append(cart_item.product.price)
            if cart_item.color_variant:
                price.append(cart_item.color_variant.price)
            if cart_item.size_variant:
                price.append(cart_item.size_variant.price)
        return sum(price)

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='cart_items', null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product} in {self.cart}"

    def get_product_price(self): 
        price = []
        if self.product:
            price.append(self.product.price)
        if self.color_variant:
            price.append(self.color_variant.price)
        if self.size_variant:
            price.append(self.size_variant.price)
        return sum(price)

@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            profile, created = Profile.objects.get_or_create(user=instance)
            if created:
                profile.email_token = email_token
                profile.save()
                send_account_activation_email(instance.email, email_token)
    except Exception as e:
        print("Error:", e)
        return False
