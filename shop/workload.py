"""
Розрахунок поточної завантаженості майстра.
"""
from .models import Order, CustomOrder

# Пороги активних замовлень
THRESHOLD_BUSY = 6  # 5+ замовлень → попередження про 2 тижні
THRESHOLD_VERY_BUSY = 10  # 10+ → 1 місяць
THRESHOLD_OVERLOADED = 20  # 20+ → блокування


def count_active_orders():
    """Кількість замовлень з каталогу, що в роботі."""
    return Order.objects.filter(
        status__in=[
            Order.Status.PENDING,
            Order.Status.PAID,
            Order.Status.IN_PROGRESS,
        ]
    ).count()


def count_active_custom_orders():
    """Кількість індивідуальних замовлень, що в роботі."""
    return CustomOrder.objects.filter(
        status__in=[
            CustomOrder.Status.NEW,
            CustomOrder.Status.IN_PROGRESS,
        ]
    ).count()


def get_workload():
    """
    Повертає dict зі статусом завантаженості майстра.
    Використовується в шаблонах та context processor.
    """
    active_orders = count_active_orders()
    active_custom = count_active_custom_orders()
    total = active_orders + active_custom

    if total >= THRESHOLD_OVERLOADED:
        return {
            'level': 'overloaded',
            'count': total,
            'title': 'Майстер тимчасово не приймає замовлення',
            'message': f'Зараз у роботі {total} замовлень. Прийом нових замовлень тимчасово припинено. Зв\'яжіться з нами для уточнення термінів.',
            'can_order': False,
            'wait_text': None,
        }
    elif total >= THRESHOLD_VERY_BUSY:
        return {
            'level': 'very_busy',
            'count': total,
            'title': 'Високе завантаження майстерні',
            'message': f'Майстер виготовляє {total} замовлень. Початок роботи над вашим — приблизно через 1 місяць.',
            'can_order': True,
            'wait_text': 'через 1 місяць',
        }
    elif total >= THRESHOLD_BUSY:
        return {
            'level': 'busy',
            'count': total,
            'title': 'Багато активних замовлень',
            'message': f'Майстер виготовляє {total} замовлень. Початок роботи над вашим — приблизно через 2 тижні.',
            'can_order': True,
            'wait_text': 'через 2 тижні',
        }
    else:
        return {
            'level': 'normal',
            'count': total,
            'title': None,
            'message': None,
            'can_order': True,
            'wait_text': 'найближчим часом',
        }