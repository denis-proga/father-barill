from django import forms
from .models import CustomOrder, ProductType, Purpose
from .models import Review
from .models import ContactMessage
from .models import Order

# Списки назначений по типу — используем в валидации
BARREL_PURPOSES = [Purpose.VODKA, Purpose.WINE, Purpose.COGNAC, Purpose.WATER, Purpose.OTHER]
DIZHKA_PURPOSES = [Purpose.CABBAGE, Purpose.TOMATO, Purpose.APPLE, Purpose.CUCUMBER, Purpose.OTHER]


class CustomOrderForm(forms.ModelForm):
    """Форма индивидуального заказа."""

    class Meta:
        model = CustomOrder
        fields = [
            'product_type',
            'purpose',
            'size_liters',
            'extra_wishes',
            'customer_name',
            'customer_phone',
            'customer_email',
        ]
        widgets = {
            'product_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'id_product_type',
            }),
            'purpose': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'id_purpose',
            }),
            'size_liters': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'min': 1,
                'max': 500,
                'placeholder': 'Наприклад: 30',
            }),
            'extra_wishes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишіть ваші побажання: гравіювання, особлива обробка, термін виготовлення тощо...',
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Іван Петренко',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+380 67 123 45 67',
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ivan@example.com',
            }),
        }
        labels = {
            'product_type': 'Що ви хочете замовити?',
            'purpose': 'Призначення',
            'size_liters': 'Об\'єм (літри)',
            'extra_wishes': 'Додаткові побажання',
            'customer_name': 'Ваше ім\'я',
            'customer_phone': 'Номер телефону',
            'customer_email': 'Email',
        }

    def clean(self):
        """Дополнительная валидация: назначение должно соответствовать типу товара."""
        cleaned_data = super().clean()
        product_type = cleaned_data.get('product_type')
        purpose = cleaned_data.get('purpose')

        if product_type == ProductType.BARREL and purpose not in BARREL_PURPOSES:
            raise forms.ValidationError(
                'Для бочки виберіть призначення: горілка, вино, коньяк, вода або інше.'
            )

        if product_type == ProductType.DIZHKA and purpose not in DIZHKA_PURPOSES:
            raise forms.ValidationError(
                'Для діжки виберіть призначення: капуста, помідори, яблука, огірки або інше.'
            )

        return cleaned_data

class ReviewForm(forms.ModelForm):
    """Форма для нового отзыва."""

    class Meta:
        model = Review
        fields = ['author_name', 'rating', 'text']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ваше ім\'я',
            }),
            'rating': forms.Select(
                choices=[(i, '★' * i + '☆' * (5 - i)) for i in range(1, 6)],
                attrs={'class': 'form-select form-select-lg'},
            ),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Поділіться вашим досвідом — що замовляли, як працює бочка...',
            }),
        }
        labels = {
            'author_name': 'Ваше ім\'я',
            'rating': 'Оцінка',
            'text': 'Ваш відгук',
        }


class ContactForm(forms.ModelForm):
    """Форма обратной связи."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Іван Петренко',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ivan@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+380 67 123 45 67',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Питання про бочку 50л',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ваше повідомлення...',
            }),
        }
        labels = {
            'name': 'Ваше ім\'я',
            'email': 'Email',
            'phone': 'Телефон (необов\'язково)',
            'subject': 'Тема',
            'message': 'Повідомлення',
        }


class CheckoutForm(forms.ModelForm):
    """Форма оформления заказа."""

    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'delivery_city', 'delivery_branch',
            'payment_method', 'customer_note',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Іван Петренко',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+380 67 123 45 67',
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ivan@example.com',
            }),
            'delivery_city': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Київ',
            }),
            'delivery_branch': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Відділення №3, вул. Хрещатик 22',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'customer_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Особливі побажання щодо доставки або замовлення...',
            }),
        }
        labels = {
            'customer_name': 'Ваше ім\'я',
            'customer_phone': 'Номер телефону',
            'customer_email': 'Email',
            'delivery_city': 'Місто',
            'delivery_branch': 'Відділення Нової Пошти',
            'payment_method': 'Спосіб оплати',
            'customer_note': 'Коментар до замовлення',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Тепер обидва способи доступні
        self.fields['payment_method'].choices = [
            (Order.PaymentMethod.LIQPAY, '💳 Картка онлайн (Visa/Mastercard через LiqPay)'),
            (Order.PaymentMethod.COD, '📦 Накладений платіж (на Нову Пошту)'),
        ]
        self.fields['payment_method'].initial = Order.PaymentMethod.LIQPAY
        self.fields['customer_note'].required = False