from django.shortcuts import render
from products.models import Product


# Create your views here.
def index(request):

    context = {
        'products': Product.objects.all()[:8],  # Fetch only the first 8 products
    }
    return render(request, 'home/index.html', context)