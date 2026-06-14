from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('custom-order/', views.custom_order, name='custom_order'),
    path('custom-order/success/', views.custom_order_success, name='custom_order_success'),
]