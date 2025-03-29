from django.shortcuts import render
from products.models import Product, SizeVariant
from django.http import Http404

def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}
        
        selected_size = request.GET.get('size', None)
        
        if selected_size:
            print(f"Selected size: {selected_size}")
            try:
                size_variant = SizeVariant.objects.get(size_name=selected_size)
                updated_price = product.price + size_variant.price
                
                context['selected_size'] = selected_size
                context['updated_price'] = updated_price
                
                print(f"Price for size {selected_size}: {updated_price}")
                
            except SizeVariant.DoesNotExist:
                print(f"Size {selected_size} not found in the database.")
        
        return render(request, 'product/product.html', context)
    
    except Product.DoesNotExist:
        raise Http404("Product not found")
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return render(request, 'product/product_not_found.html')
