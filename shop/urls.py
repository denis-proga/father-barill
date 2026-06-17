from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('custom-order/', views.custom_order, name='custom_order'),
    path('custom-order/success/', views.custom_order_success, name='custom_order_success'),
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/success/', views.review_success, name='review_success'),
    path('contacts/', views.contacts, name='contacts'),
    path('contacts/success/', views.contacts_success, name='contacts_success'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/', views.order_success, name='order_success'),
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/result/', views.payment_result, name='payment_result'),
    path('support/', views.support, name='support'),
    path('api/np/cities/', views.np_cities_search, name='np_cities'),
    path('api/np/warehouses/', views.np_warehouses, name='np_warehouses'),
]