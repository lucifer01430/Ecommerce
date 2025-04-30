from django.db import models
from django.contrib.auth.models import User
from products.models import Product, SizeVariant, ColorVariant
import uuid
from decimal import Decimal

ORDER_STATUS = (
    ('Pending', 'Pending'),
    ('Placed', 'Placed'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled')
)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uid = models.UUIDField(null=True, blank=True, editable=False, unique=True)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=100, default="COD")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Changed to DecimalField
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.short_order_id} by {self.user.username}"

    @property
    def short_order_id(self):
        return f"ORD{str(self.id).zfill(6)}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)    # New field
    taxable_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)        # New field
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)        # New field
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field

    def __str__(self):
        return f"{self.product} ({self.quantity})"

    def get_product_price(self):
        price = self.product.price if self.product else Decimal('0.00')
        if self.size_variant:
            price += self.size_variant.price
        if self.color_variant:
            price += self.color_variant.price
        return price * Decimal(str(self.quantity))  # Ensure quantity is treated as Decimal