from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Product, Order, OrderItem
from django.db import connections
from accounts.models import BonusCard
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from accounts.models import Address

def index(request):
    POPULAR_EXTERNAL_IDS = [1, 2, 3]  # те, что ты хочешь показывать
    popular_items = Product.objects.filter(external_id__in=POPULAR_EXTERNAL_IDS)  

    return render(request, 'index.html', {
        'popular_items': popular_items
    })



def shop(request):
    return render(request, 'shop.html')

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def contact(request):
    return render(request, 'contact.html')



def cart(request):
    cart = request.session.get('cart', {})
    use_bonus = request.session.get('use_bonus', False)

    cart_items = []
    total_price_before_card_discount = Decimal('0.00')

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, pk=product_id)

        # 1. Цена с учетом скидки на товар
        price_after_product_discount = product.get_discounted_price()

        # Сумма без скидки карты
        item_total = price_after_product_discount * qty
        total_price_before_card_discount += item_total

        cart_items.append({
            'product': product,
            'quantity': qty,
            'discounted_price': price_after_product_discount,
            'original_price': product.price,
            'item_total': item_total,
        })

    discount_amount = Decimal('0.00')
    bonus_to_use = Decimal('0.00')
    final_price = total_price_before_card_discount
    bonus_points = Decimal('0.00')
    bonus_card = None

    if request.user.is_authenticated:
        try:
            bonus_card = BonusCard.objects.get(user=request.user)

            # 2. Применяем скидку по карте на сумму уже со скидками на товары
            discount_percent = Decimal(bonus_card.discount_percent)
            discount_amount = (discount_percent / 100) * final_price
            final_price -= discount_amount

            # 3. Применяем бонусы
            bonus_points = Decimal(bonus_card.bonus_points)
            if use_bonus:
                bonus_to_use = min(bonus_points, final_price)
                final_price -= bonus_to_use

        except BonusCard.DoesNotExist:
            pass
        addresses = Address.objects.filter(user=request.user)
    else:
        addresses = []

    if request.method == 'POST':
        address_id = request.POST.get('address')
        if address_id:
            try:
                selected_address = Address.objects.get(pk=address_id, user=request.user)

            # Создаём заказ
                order = Order.objects.create(
                    user=request.user,
                    address=selected_address,
                    total=final_price
                    )

            # Сохраняем товары из корзины
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['discounted_price']
                        )

            # Очищаем корзину и бонусы
                request.session['cart'] = {}
                request.session['use_bonus'] = False

                return redirect('order_success', order_id=order.id)

            except Address.DoesNotExist:
                request.session['error_message'] = "Выберите корректный адрес."
                return redirect('cart')

    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price_before_card_discount,
        'discount_amount': discount_amount,
        'bonus_to_use': bonus_to_use,
        'final_price': final_price,
        'bonus_points': bonus_points,
        'bonus_card': bonus_card,
        'use_bonus': use_bonus,
        'error_message': request.session.pop('error_message', None),
        'addresses': addresses,
    })

def contact(request):
    return render(request, 'contact.html')

def category_view(request, category):
    subcategory = request.GET.get('subcategory')
    subcategory_display = {
        'lipstick': 'Помады',
        'mascara': 'Тушь для ресниц',
        'eyeshadow': 'Тени для век',
    }

    if category == 'decorative':
        # Получаем все подкатегории, чтобы их показать
        subcategories = Product.objects.filter(category='decorative') \
                                       .values_list('subcategory', flat=True).distinct()

        if subcategory:
            # Пользователь выбрал подкатегорию → показываем товары
            products_qs = Product.objects.filter(category='decorative', subcategory=subcategory).order_by('id')
            paginator = Paginator(products_qs, 8)
            page_obj = paginator.get_page(request.GET.get('page'))

            # Корзина
            cart = request.session.get('cart', {})
            for prod in page_obj:
                prod.in_cart = cart.get(str(prod.id), 0)
        else:
            # Подкатегория не выбрана → ничего не показываем
            page_obj = None

    else:
        # Уходовая косметика → обычный список товаров
        products_qs = Product.objects.filter(category=category).order_by('id')
        subcategories = None
        paginator = Paginator(products_qs, 8)
        page_obj = paginator.get_page(request.GET.get('page'))

        # Корзина
        cart = request.session.get('cart', {})
        for prod in page_obj:
            prod.in_cart = cart.get(str(prod.id), 0)

    return render(request, 'shop_by_category.html', {
        'page_obj': page_obj,
        'category_code': category,
        'subcategories': subcategories,
        'subcategory': subcategory,
        'subcategory_display': subcategory_display,
    })





@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    product = get_object_or_404(Product, id=product_id)
    current_quantity = cart.get(product_id, 0)

    # проверяем остаток
    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1
        request.session['cart'] = cart
    else:
        # можно сохранить сообщение в сессии или вывести позже
        request.session['cart_error'] = f"На складе только {product.stock} шт. товара «{product.name}»"

    return redirect(request.META.get('HTTP_REFERER', 'shop'))

def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})
    error_message = None

    if request.method == 'POST':
        action = request.POST.get('action')
        current_quantity = cart.get(str(product_id), 0)

        if action == 'increase':
            if current_quantity < product.stock:
                cart[str(product_id)] = current_quantity + 1
            else:
                error_message = f"На складе только {product.stock} шт."

        elif action == 'decrease':
            if current_quantity > 1:
                cart[str(product_id)] = current_quantity - 1
            else:
                cart.pop(str(product_id), None)

        elif action == 'remove':
            cart.pop(str(product_id), None)

        request.session['cart'] = cart

        # Сохраняем сообщение об ошибке (если есть)
        if error_message:
            request.session['error_message'] = error_message

    return redirect('cart')

@require_POST
def update_cart_ajax(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})
    pid = str(product_id)
    action = request.POST.get('action')
    qty = cart.get(pid, 0)

    if action in ('add', 'increase'):
        if qty < product.stock:
            qty += 1
    elif action == 'decrease':
        qty = qty - 1 if qty > 1 else 0

    if qty > 0:
        cart[pid] = qty
    else:
        cart.pop(pid, None)

    request.session['cart'] = cart
    return JsonResponse({'success': True, 'quantity': qty})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review
from .forms import ReviewForm  # не забудь создать этот файл, если ещё не создал

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем количество товара в корзине
    cart = request.session.get('cart', {})
    quantity = cart.get(str(product.id), 0)  # Ключевое исправление!
    
    reviews = product.reviews.all().order_by('-created_at')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.email = request.user.email
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'product_detail.html', {
        'product': product,
        'quantity': quantity,  # Теперь передаем количество в контекст
        'reviews': reviews,
        'form': form,
    })


def update_stock_in_orders_db(product_id, new_stock):
    cursor = connections['stock_db'].cursor()
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", [new_stock, product_id])



def checkout(request):
    use_bonus = request.POST.get('use_bonus') == 'on'
    request.session['use_bonus'] = use_bonus
    return render(request, 'checkout.html')

@csrf_exempt
def toggle_bonus(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        use_bonus = data.get('use_bonus', False)
        request.session['use_bonus'] = use_bonus

        cart = request.session.get('cart', {})
        total_price = Decimal('0.00')

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            discounted_price = product.get_discounted_price()
            total_price += discounted_price * quantity  # сумма уже со скидками из админки

        try:
            bonus_card = BonusCard.objects.get(user=request.user)
            # Скидка по карте уже на сумму со скидками из админки
            discount_amount = (Decimal(bonus_card.discount_percent) / 100) * total_price
            final_price = max(total_price - discount_amount, 0)

            bonus_to_use = Decimal('0.00')
            if use_bonus:
                bonus_to_use = min(Decimal(bonus_card.bonus_points), final_price)
                final_price -= bonus_to_use

            return JsonResponse({
                'final_price': f'{final_price:.2f}',
                'bonus_to_use': f'{bonus_to_use:.2f}'
            })

        except BonusCard.DoesNotExist:
            return JsonResponse({'final_price': f'{total_price:.2f}'})

    return JsonResponse({'error': 'Invalid request'}, status=400)



