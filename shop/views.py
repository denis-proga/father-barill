from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, ProductType, Purpose


def home(request):
    """Главная страница."""
    latest_products = Product.objects.filter(is_active=True)[:6]
    return render(request, 'shop/home.html', {'latest_products': latest_products})


def catalog(request):
    """Каталог товаров с фильтрами и пагинацией."""
    products = Product.objects.filter(is_active=True)

    # === Фильтр по типу (бочка/діжка) ===
    current_type = request.GET.get('type', '')
    if current_type in ProductType.values:
        products = products.filter(product_type=current_type)

    # === Фильтр по назначению ===
    current_purpose = request.GET.get('purpose', '')
    if current_purpose in Purpose.values:
        products = products.filter(purpose=current_purpose)

    # === Сортировка ===
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'size_asc':
        products = products.order_by('size_liters')
    elif sort == 'size_desc':
        products = products.order_by('-size_liters')
    else:  # newest
        products = products.order_by('-created_at')

    # === Пагинация: 9 товаров на страницу ===
    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    # === Доступные назначения зависят от типа (для UI) ===
    if current_type == ProductType.BARREL:
        available_purposes = [
            (Purpose.VODKA, 'Горілка'),
            (Purpose.WINE, 'Вино'),
            (Purpose.COGNAC, 'Коньяк'),
            (Purpose.WATER, 'Вода'),
            (Purpose.OTHER, 'Інше'),
        ]
    elif current_type == ProductType.DIZHKA:
        available_purposes = [
            (Purpose.CABBAGE, 'Капуста'),
            (Purpose.TOMATO, 'Помідори'),
            (Purpose.APPLE, 'Яблука'),
            (Purpose.CUCUMBER, 'Огірки'),
            (Purpose.OTHER, 'Інше'),
        ]
    else:
        available_purposes = Purpose.choices

    context = {
        'page_obj': page_obj,
        'current_type': current_type,
        'current_purpose': current_purpose,
        'current_sort': sort,
        'available_purposes': available_purposes,
        'total_count': paginator.count,
    }
    return render(request, 'shop/catalog.html', context)


def product_detail(request, pk):
    """Страница одного товара."""
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # Похожие товары: того же типа, исключая текущий
    related_products = Product.objects.filter(
        is_active=True,
        product_type=product.product_type
    ).exclude(pk=product.pk)[:3]

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })