from django.db import models
from base.models import BaseModel
from django.utils.text import slugify

class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.category_name)  
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:  
        return self.category_name


class ColorVariant(BaseModel):  
    color_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self) -> str:  
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self) -> str:   
        return self.size_name


class Product(BaseModel):
    product_name = models.CharField(max_length=100)    
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()
    color_varient = models.ManyToManyField('ColorVariant', blank=True)
    size_variant = models.ManyToManyField('SizeVariant', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.product_name)  
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:  
        return self.product_name

    def get_product_price_by_size(self, size_name):
        try:
            size_variant = SizeVariant.objects.get(size_name=size_name)
            return self.price + size_variant.price
        except SizeVariant.DoesNotExist:
            return self.price  


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='products')
