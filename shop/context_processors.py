from .cart import Cart


def cart(request):
    """Робить корзину доступною у всіх шаблонах як змінну {{ cart }}."""
    return {'cart': Cart(request)}