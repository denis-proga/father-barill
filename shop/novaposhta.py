"""
Nova Poshta API client.
Документація: https://developers.novaposhta.ua/
"""
import requests
from django.conf import settings


def _call(model_name: str, called_method: str, properties: dict = None) -> list:
    """
    Універсальний виклик до Nova Poshta API.

    Повертає список результатів або порожній список при помилці.
    """
    payload = {
        'apiKey': settings.NOVAPOSHTA_API_KEY,
        'modelName': model_name,
        'calledMethod': called_method,
        'methodProperties': properties or {},
    }

    try:
        response = requests.post(
            settings.NOVAPOSHTA_API_URL,
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            return result.get('data', [])

        # Лог помилок API
        print('[Nova Poshta] API errors:', result.get('errors', []))
        return []

    except Exception as e:
        print(f'[Nova Poshta] Request failed: {e}')
        return []


def search_cities(query: str, limit: int = 10) -> list[dict]:
    """
    Шукати міста по префіксу назви.
    Повертає [{Ref, Description, ...}, ...].

    Приклад: search_cities("Льв") → [{"Ref": "...", "Description": "Львів"}, ...]
    """
    if len(query) < 2:
        return []

    return _call('Address', 'getCities', {
        'FindByString': query,
        'Page': '1',         # ← теперь строка, как ожидает Nova Poshta
        'Limit': str(limit),
    })


def get_warehouses(city_ref: str) -> list[dict]:
    """
    Отримати всі відділення Нової Пошти у місті.

    city_ref — UUID міста з search_cities (поле Ref).
    Повертає [{Ref, Description, Number, ShortAddress, ...}, ...].
    """
    if not city_ref:
        return []

    return _call('AddressGeneral', 'getWarehouses', {
        'CityRef': city_ref,
    })