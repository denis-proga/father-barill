"""
Sitemap для пошукових систем.
Описує які URL існують на сайті та як часто оновлюються.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product


class StaticPagesSitemap(Sitemap):
    """Статичні сторінки сайту."""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'catalog',
            'custom_order',
            'reviews',
            'contacts',
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Карточки товарів — динамічно з БД."""
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('product_detail', kwargs={'pk': obj.id})