from django.urls import path
from home.views import index
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('', views.home, name='home'),
]

