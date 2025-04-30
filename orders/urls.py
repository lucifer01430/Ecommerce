from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('invoice/<uuid:uid>/', views.download_invoice, name='download_invoice'),
    path('invoice-preview/<uuid:uid>/', views.preview_invoice, name='preview_invoice'),



]
