"""
LiqPay integration — генерація платіжних запитів та перевірка вебхуків.

Документація: https://www.liqpay.ua/documentation/api/aquiring/checkout/doc
"""
import base64
import hashlib
import json
from django.conf import settings


def _b64_encode_json(payload: dict) -> str:
    """Закодувати dict у base64-string для LiqPay."""
    json_str = json.dumps(payload)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')


def _sign(data: str) -> str:
    """
    Створити криптографічний підпис LiqPay.
    Формула: base64(SHA1(private_key + data + private_key))
    """
    private_key = settings.LIQPAY_PRIVATE_KEY
    raw = (private_key + data + private_key).encode('utf-8')
    sha1_digest = hashlib.sha1(raw).digest()
    return base64.b64encode(sha1_digest).decode('utf-8')


def generate_payment(order, base_url: str) -> tuple[str, str]:
    """
    Створити (data, signature) для платежу.

    base_url — повна URL нашого сайту, наприклад 'http://127.0.0.1:8000'.
    Потрібен щоб LiqPay знав куди робити redirect та webhook.
    """
    payload = {
        'public_key': settings.LIQPAY_PUBLIC_KEY,
        'version': '3',
        'action': 'pay',
        'amount': str(order.total_price),
        'currency': 'UAH',
        'description': f'Замовлення №{order.id} — Дубові бочки',
        'order_id': str(order.id),
        'language': 'uk',
        'result_url': f'{base_url}/payment/result/',
        'server_url': f'{base_url}/payment/callback/',
    }

    # У dev-режимі додаємо прапор sandbox — LiqPay не списує реальні гроші
    if settings.LIQPAY_SANDBOX:
        payload['sandbox'] = 1

    data = _b64_encode_json(payload)
    signature = _sign(data)

    return data, signature


def verify_signature(data: str, signature: str) -> bool:
    """
    Перевірити підпис вебхука від LiqPay.
    Якщо хтось підробить запит на наш callback без знання private_key — підпис не співпаде.
    """
    expected_signature = _sign(data)
    return expected_signature == signature


def parse_callback(data: str) -> dict:
    """Розкодувати base64-data з вебхука у dict."""
    decoded_json = base64.b64decode(data).decode('utf-8')
    return json.loads(decoded_json)