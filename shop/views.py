from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, ProductType, Purpose
from django.shortcuts import redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from .forms import CustomOrderForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import ContactForm
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .liqpay import generate_payment, verify_signature, parse_callback
from django.http import JsonResponse
from .novaposhta import search_cities, get_warehouses


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


def custom_order(request):
    """Конструктор индивидуального заказа."""
    if request.method == 'POST':
        form = CustomOrderForm(request.POST)
        if form.is_valid():
            order = form.save()

            # Відправляємо email майстру
            send_mail(
                subject=f'Нове замовлення №{order.id} від {order.customer_name}',
                message=render_to_string('shop/emails/order_to_master.txt', {'order': order}),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.MASTER_EMAIL],
                fail_silently=False,
            )

            # Відправляємо підтвердження клієнту
            send_mail(
                subject=f'Замовлення №{order.id} прийнято — Дубові бочки',
                message=render_to_string('shop/emails/order_to_client.txt', {'order': order}),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.customer_email],
                fail_silently=False,
            )

            return redirect('custom_order_success')
    else:
        form = CustomOrderForm()

    return render(request, 'shop/custom_order.html', {'form': form})


def custom_order_success(request):
    """Страница 'Дякуємо за замовлення'."""
    return render(request, 'shop/custom_order_success.html')


def reviews(request):
    """Список отзывов + форма добавления."""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False  # На модерации
            review.save()

            # Email майстру про новий відгук
            send_mail(
                subject=f'Новий відгук від {review.author_name}',
                message=f'Новий відгук на модерації:\n\n'
                        f'Від: {review.author_name}\n'
                        f'Оцінка: {review.rating}/5\n\n'
                        f'{review.text}\n\n'
                        f'Перейти до модерації: http://127.0.0.1:8000/admin/shop/review/{review.id}/change/',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.MASTER_EMAIL],
                fail_silently=False,
            )

            return redirect('review_success')
    else:
        form = ReviewForm()

    # Показываем только одобренные отзывы
    approved_reviews = Review.objects.filter(is_approved=True)

    # Считаем статистику
    avg_rating = None
    if approved_reviews.exists():
        total = sum(r.rating for r in approved_reviews)
        avg_rating = round(total / approved_reviews.count(), 1)

    context = {
        'reviews': approved_reviews,
        'form': form,
        'avg_rating': avg_rating,
        'reviews_count': approved_reviews.count(),
    }
    return render(request, 'shop/reviews.html', context)


def review_success(request):
    """Спасибо за отзыв."""
    return render(request, 'shop/review_success.html')


def contacts(request):
    """Страница контактов с формой обратной связи."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save()

            # Email майстру
            send_mail(
                subject=f'Нове повідомлення: {msg.subject}',
                message=render_to_string('shop/emails/contact_to_master.txt', {'msg': msg}),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.MASTER_EMAIL],
                fail_silently=False,
            )

            return redirect('contacts_success')
    else:
        form = ContactForm()

    return render(request, 'shop/contacts.html', {'form': form})


def contacts_success(request):
    """Спасибо за сообщение."""
    return render(request, 'shop/contacts_success.html')

@require_POST
def cart_add(request, product_id):
    """Додати товар до корзини (POST only)."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity=quantity)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    """Видалити товар з корзини."""
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart_detail')


@require_POST
def cart_update(request, product_id):
    """Оновити кількість товару."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart.add(product, quantity=quantity, override_quantity=True)
    else:
        cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    """Сторінка корзини."""
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


def checkout(request):
    """Оформлення замовлення з вибором способу оплати."""
    cart = Cart(request)

    if len(cart) == 0:
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price_at_purchase=item['price'],
                )

            # Запам'ятовуємо id замовлення для наступних сторінок
            request.session['last_order_id'] = order.id

            # === LiqPay flow ===
            if order.payment_method == Order.PaymentMethod.LIQPAY:
                # Не очищаємо корзину тут — чекаємо підтвердження оплати
                # Email теж не шлемо — тільки після успішної оплати
                return redirect('payment_page')

            # === COD flow (старий) ===
            else:
                send_order_emails(order)
                cart.clear()
                return redirect('order_success')
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart': cart,
    })


def send_order_emails(order):
    """Helper для відправки email при новому замовленні."""
    # Майстру
    send_mail(
        subject=f'Нове замовлення №{order.id} від {order.customer_name}',
        message=render_to_string('shop/emails/order_to_master_full.txt', {'order': order}),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.MASTER_EMAIL],
        fail_silently=False,
    )

    # Клієнту
    send_mail(
        subject=f'Замовлення №{order.id} прийнято — Дубові бочки',
        message=render_to_string('shop/emails/order_to_customer_full.txt', {'order': order}),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        fail_silently=False,
    )


def order_success(request):
    """Сторінка 'Дякуємо за замовлення'."""
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})


def payment_page(request):
    """Сторінка з LiqPay формою (auto-submit на LiqPay)."""
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, status=Order.Status.PENDING)

    # Будуємо абсолютну URL нашого сайту для callbacks
    base_url = request.build_absolute_uri('/').rstrip('/')

    data, signature = generate_payment(order, base_url=base_url)

    return render(request, 'shop/payment_page.html', {
        'order': order,
        'data': data,
        'signature': signature,
        'checkout_url': settings.LIQPAY_CHECKOUT_URL,
    })


@csrf_exempt
def payment_callback(request):
    """
    Webhook від LiqPay (server_url).
    LiqPay POST'ить сюди підтвердження оплати з підписом.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    data = request.POST.get('data', '')
    signature = request.POST.get('signature', '')

    if not data or not signature:
        return HttpResponse('Missing data', status=400)

    # Перевіряємо підпис — гарантія що дані від LiqPay, а не від хакера
    if not verify_signature(data, signature):
        return HttpResponse('Invalid signature', status=400)

    payment = parse_callback(data)
    order_id = payment.get('order_id')
    status = payment.get('status', '')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse('Order not found', status=404)

    # Успішні статуси LiqPay
    if status in ('success', 'sandbox', 'wait_accept'):
        # Захист від подвійного оновлення (LiqPay може прислати webhook двічі)
        if order.status == Order.Status.PENDING:
            order.status = Order.Status.PAID
            order.save()
            send_order_emails(order)

    # Невдалі статуси
    elif status in ('failure', 'error', 'reversed'):
        if order.status == Order.Status.PENDING:
            order.status = Order.Status.CANCELLED
            order.save()

    # LiqPay чекає відповіді 200 OK — інакше буде ретраїти webhook
    return HttpResponse('OK')


def payment_result(request):
    """
    Сторінка куди потрапляє клієнт ПІСЛЯ оплати (result_url).
    Показуємо статус залежно від того що в БД.
    """
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)

    if order.status == Order.Status.PAID:
        # Оплата підтверджена через webhook → показуємо успіх
        Cart(request).clear()
        return render(request, 'shop/order_success.html', {'order': order})

    elif order.status == Order.Status.CANCELLED:
        return render(request, 'shop/payment_failed.html', {'order': order})

    else:
        # Статус досі PENDING — webhook ще не прийшов
        return render(request, 'shop/payment_pending.html', {'order': order})

def support(request):
    """Сторінка технічної підтримки сайту."""
    return render(request, 'shop/support.html')

def robots_txt(request):
    """Файл robots.txt для пошукових систем."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "Disallow: /payment/",
        "Disallow: /order/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def np_cities_search(request):
    """API: пошук міст Нової Пошти за префіксом."""
    query = request.GET.get('q', '').strip()

    cities = search_cities(query, limit=10)

    # Спрощуємо формат для frontend
    results = [
        {
            'ref': city.get('Ref'),
            'name': city.get('Description'),
            'area': city.get('AreaDescription'),
        }
        for city in cities
    ]

    return JsonResponse({'results': results})


def np_warehouses(request):
    """API: отримати відділення для конкретного міста."""
    city_ref = request.GET.get('city_ref', '').strip()

    warehouses = get_warehouses(city_ref)

    results = [
        {
            'ref': wh.get('Ref'),
            'name': wh.get('Description'),
            'number': wh.get('Number'),
            'address': wh.get('ShortAddress'),
        }
        for wh in warehouses
    ]

    return JsonResponse({'results': results})