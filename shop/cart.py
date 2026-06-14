from decimal import Decimal
from .models import Product


class Cart:
    """
    Сессионная корзина.
    Хранится в request.session['cart'] как словарь:
    {
        '15': {'quantity': 2, 'price': '5000.00'},
        '18': {'quantity': 1, 'price': '8500.00'},
    }
    Ключи — id товара (строкой, чтобы JSON-сериализация работала).
    """

    SESSION_KEY = 'cart'

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Додати товар або оновити кількість."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        """Видалити товар з корзини."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Помітити сесію зміненою щоб Django зберіг."""
        self.session.modified = True

    def __iter__(self):
        """
        Ітерація по корзині з підвантаженням об'єктів Product з БД.
        Дозволяє в шаблоні писати: {% for item in cart %} ... {{ item.product.name }}
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Загальна кількість одиниць товару (для лічильника в навбарі)."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Загальна сума корзини."""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """Очистити корзину (після оформлення замовлення)."""
        if self.SESSION_KEY in self.session:
            del self.session[self.SESSION_KEY]
            self.save()