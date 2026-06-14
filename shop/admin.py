from django.contrib import admin
from .models import Product, ProductImage, CustomOrder, Review
from .models import ContactMessage
from .models import Order, OrderItem


# ============================================================
# Inline — позволяет редактировать фото прямо на странице товара
# ============================================================

class ProductImageInline(admin.TabularInline):
    """Дополнительные фото товара — отображаются на странице товара."""
    model = ProductImage
    extra = 3  # сколько пустых форм для новых фото показывать


# ============================================================
# Product Admin
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'purpose', 'size_liters', 'price', 'is_active', 'created_at')
    list_filter = ('product_type', 'purpose', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active')
    inlines = [ProductImageInline]

    fieldsets = (
        ('Основне', {
            'fields': ('product_type', 'name', 'purpose', 'size_liters', 'price')
        }),
        ('Опис та фото', {
            'fields': ('description', 'main_image')
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )


# ============================================================
# CustomOrder Admin
# ============================================================

@admin.register(CustomOrder)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'product_type', 'size_liters', 'status', 'created_at')
    list_filter = ('status', 'product_type', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email')
    list_editable = ('status',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Клієнт', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Замовлення', {
            'fields': ('product_type', 'purpose', 'size_liters', 'extra_wishes')
        }),
        ('Статус', {
            'fields': ('status', 'created_at')
        }),
    )


# ============================================================
# Review Admin
# ============================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('author_name', 'text')
    list_editable = ('is_approved',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'phone', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Контактна особа', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Повідомлення', {
            'fields': ('subject', 'message')
        }),
        ('Статус', {
            'fields': ('is_read', 'created_at')
        }),
    )


class OrderItemInline(admin.TabularInline):
    """Позиции заказа — на странице заказа."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_purchase', 'get_total_price')
    fields = ('product', 'quantity', 'price_at_purchase', 'get_total_price')

    def get_total_price(self, obj):
        if obj.id:
            return f'{obj.total_price()} ₴'
        return '—'

    get_total_price.short_description = 'Сума'

    def has_add_permission(self, request, obj=None):
        # Заборона додавати позиції вручну (тільки через сайт)
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'customer_phone',
        'total_price', 'payment_method', 'status', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email', 'tracking_number')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Клієнт', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Доставка', {
            'fields': ('delivery_city', 'delivery_branch', 'tracking_number')
        }),
        ('Замовлення', {
            'fields': ('total_price', 'payment_method', 'status', 'customer_note')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
