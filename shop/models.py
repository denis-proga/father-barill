from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================================================
# CHOICES — фиксированные списки значений
# ============================================================

class ProductType(models.TextChoices):
    """Тип изделия — бочка или діжка."""
    BARREL = 'barrel', 'Бочка'
    DIZHKA = 'dizhka', 'Діжка'


class Purpose(models.TextChoices):
    """Назначение изделия."""
    # Для бочек
    VODKA = 'vodka', 'Горілка'
    WINE = 'wine', 'Вино'
    COGNAC = 'cognac', 'Коньяк'
    WATER = 'water', 'Вода'
    # Для діжок
    CABBAGE = 'cabbage', 'Капуста'
    TOMATO = 'tomato', 'Помідори'
    APPLE = 'apple', 'Яблука'
    CUCUMBER = 'cucumber', 'Огірки'
    # Универсальное
    OTHER = 'other', 'Інше'


# Какие назначения подходят для какого типа товара
# Используется в валидации и формах
PURPOSE_BY_TYPE = {
    ProductType.BARREL: [Purpose.VODKA, Purpose.WINE, Purpose.COGNAC, Purpose.WATER, Purpose.OTHER],
    ProductType.DIZHKA: [Purpose.CABBAGE, Purpose.TOMATO, Purpose.APPLE, Purpose.CUCUMBER, Purpose.OTHER],
}


# ============================================================
# Product — основная модель товара (бочка или діжка)
# ============================================================

class Product(models.Model):
    """Товар в каталоге — готовая бочка или діжка."""

    product_type = models.CharField(
        max_length=10,
        choices=ProductType.choices,
        verbose_name='Тип виробу'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Назва'
    )

    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        verbose_name='Призначення'
    )

    size_liters = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(500)],
        verbose_name='Об\'єм (літри)'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Ціна (грн)'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Опис'
    )

    main_image = models.ImageField(
        upload_to='products/',
        verbose_name='Головне фото'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Показувати на сайті'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Створено'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Оновлено'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_product_type_display()} "{self.name}" — {self.size_liters}л'


# ============================================================
# ProductImage — дополнительные фото для галереи товара
# ============================================================

class ProductImage(models.Model):
    """Дополнительные фото товара (галерея)."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )

    image = models.ImageField(
        upload_to='products/gallery/',
        verbose_name='Фото'
    )

    class Meta:
        verbose_name = 'Фото товару'
        verbose_name_plural = 'Фото товарів'

    def __str__(self):
        return f'Фото для {self.product.name}'


# ============================================================
# CustomOrder — индивидуальный заказ через конструктор
# ============================================================

class CustomOrder(models.Model):
    """Индивидуальный заказ — клиент задаёт параметры сам."""

    class Status(models.TextChoices):
        NEW = 'new', 'Нове'
        IN_PROGRESS = 'in_progress', 'В роботі'
        READY = 'ready', 'Готове'
        SHIPPED = 'shipped', 'Відправлено'
        CLOSED = 'closed', 'Закрито'

    customer_name = models.CharField(max_length=100, verbose_name='Ім\'я клієнта')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    customer_email = models.EmailField(verbose_name='Email')

    product_type = models.CharField(
        max_length=10,
        choices=ProductType.choices,
        verbose_name='Тип виробу'
    )

    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        verbose_name='Призначення'
    )

    size_liters = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(500)],
        verbose_name='Об\'єм (літри)'
    )

    extra_wishes = models.TextField(
        blank=True,
        verbose_name='Додаткові побажання'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')

    class Meta:
        verbose_name = 'Індивідуальне замовлення'
        verbose_name_plural = 'Індивідуальні замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення #{self.id} — {self.customer_name} ({self.size_liters}л)'


# ============================================================
# Review — отзыв клиента
# ============================================================

class Review(models.Model):
    """Отзыв клиента о работе мастера."""

    author_name = models.CharField(max_length=100, verbose_name='Ім\'я автора')
    text = models.TextField(verbose_name='Текст відгуку')

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оцінка (1-5)'
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name='Опубліковано'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Відгук від {self.author_name} ({self.rating}★)'


# ============================================================
# ContactMessage — повідомлення з форми зворотного зв'язку
# ============================================================

class ContactMessage(models.Model):
    """Сообщение от клиента через форму контактов."""

    name = models.CharField(max_length=100, verbose_name='Ім\'я')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    subject = models.CharField(max_length=200, verbose_name='Тема')
    message = models.TextField(verbose_name='Повідомлення')

    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')

    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Від {self.name} — {self.subject}'


# ============================================================
# Order — замовлення з каталогу (повна корзина)
# ============================================================

class Order(models.Model):
    """Замовлення з звичайного каталогу (не індивідуальне)."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Очікує оплати'
        PAID = 'paid', 'Оплачено'
        IN_PROGRESS = 'in_progress', 'В обробці'
        SHIPPED = 'shipped', 'Відправлено'
        DELIVERED = 'delivered', 'Доставлено'
        CANCELLED = 'cancelled', 'Скасовано'

    class PaymentMethod(models.TextChoices):
        LIQPAY = 'liqpay', 'LiqPay (картка)'
        COD = 'cod', 'Накладений платіж'

    # Клиент
    customer_name = models.CharField(max_length=100, verbose_name='Ім\'я клієнта')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    customer_email = models.EmailField(verbose_name='Email')

    # Доставка
    delivery_city = models.CharField(max_length=100, verbose_name='Місто')
    delivery_branch = models.CharField(max_length=200, verbose_name='Відділення Нової Пошти')

    # Заказ
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Загальна сума')
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name='Спосіб оплати'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )

    # Доп.
    customer_note = models.TextField(blank=True, verbose_name='Коментар клієнта')
    tracking_number = models.CharField(max_length=50, blank=True, verbose_name='ТТН Нової Пошти')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення №{self.id} — {self.customer_name}'


class OrderItem(models.Model):
    """Позиція в замовленні — конкретна бочка з його кількістю."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Замовлення'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Ціна на момент покупки'
    )

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    def total_price(self):
        """Сума по цій позиції (ціна × кількість)."""
        return self.price_at_purchase * self.quantity