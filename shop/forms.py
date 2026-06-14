from django import forms
from .models import CustomOrder, ProductType, Purpose

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