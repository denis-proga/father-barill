from .cart import Cart
from .workload import get_workload


def cart(request):
    """Корзина доступна у всіх шаблонах."""
    return {'cart': Cart(request)}


def workload(request):
    """Статус завантаженості майстра доступний у всіх шаблонах."""
    return {'workload': get_workload()}