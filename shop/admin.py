from django.contrib import admin
from .models import Product, ProductImage, CustomOrder, Review


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
