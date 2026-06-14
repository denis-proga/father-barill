from django.shortcuts import render
from .models import Product


def home(request):
    """Главная страница."""
    # Берём 6 последних активных товаров для секции "Останні роботи"
    latest_products = Product.objects.filter(is_active=True)[:6]

    context = {
        'latest_products': latest_products,
    }
    return render(request, 'shop/home.html', context)
