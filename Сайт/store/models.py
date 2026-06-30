from django.db import models
from django.db import connections
from django.conf import settings
from django.contrib.auth.models import User
from better_profanity import profanity
import os
import sqlite3
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Address
from pathlib import Path

# Укажем путь к файлу со словами
BAD_WORDS_PATH = os.path.join(os.path.dirname(__file__), 'bad_words.txt')
profanity.load_censor_words_from_file(BAD_WORDS_PATH)


def reduce_stock(product_id, quantity):
    with connections['stock_db'].cursor() as cursor:
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", [product_id, quantity])


class Product(models.Model):
    USE_COMMON_DB = True 
    CATEGORY_CHOICES = [
        ('decorative', 'Декоративная косметика'),
        ('skincare', 'Уходовая косметика'),
    ]

    SUBCATEGORY_CHOICES = [
        ('lipstick', 'Помады'),
        ('eyeshadow', 'Тени'),
        ('mascara', 'Тушь'),
        ('none', 'Без подкатегории'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    external_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name='ID для связки с тг')
    description = models.TextField(verbose_name='Описание')
    short_description = models.CharField(max_length=255, blank=True, verbose_name='Краткое описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Скидка на этот товар', help_text="Скидка в процентах (например, 10.00 для 10%)")
    main_image = models.ImageField(upload_to='product_images/', verbose_name='Главное фото')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    subcategory = models.CharField(max_length=20, choices=SUBCATEGORY_CHOICES, default='none', verbose_name='Подкатегория')
    # Смена базы данных
    USE_COMMON_DB = True  # True = общая база, False = локальная

    @property
    def stock(self):
        # Выбираем путь
        if self.USE_COMMON_DB:
            db_path = Path(settings.STOCK_DB_PATH).resolve() # Общая база
        else:
            # Локальная база (обязательно Path.resolve())
            db_path = (Path(settings.BASE_DIR).parent / "Бот в тг" / "local_orders.db").resolve()

        print("Используемая база:", db_path, "Существует?", db_path.exists())

        # Если база не найдена, возвращаем 0
        if not db_path.exists():
            return 0

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT stock FROM products WHERE id = ?", (self.id,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else 0
        except sqlite3.Error as e:
            print("Ошибка подключения к базе:", e)
            return 0


    def get_discounted_price(self):
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price



    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Товары"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='Продукт')
    image = models.ImageField(upload_to='product_images/extra/', verbose_name='Фотки для галереи')

    def __str__(self):
        return f"Image for {self.product.name}"
    class Meta:
        verbose_name_plural = "Фотки для галереи"
    

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField()
    text = models.TextField("Отзыв")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка (1-5 звёзд)",
        default=5
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.text = profanity.censor(self.text)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} — {self.rating}★"
    
    class Meta:
        verbose_name_plural = "Отзывы"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='Пользователь')
    address = models.ForeignKey(Address, on_delete=models.PROTECT,verbose_name='Адрес')
    total = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='Итоговая сумма')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Время оформления заказа')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for item in self.items.all():
            reduce_stock(item.product.external_id, item.quantity)

    def __str__(self):
        return f"Заказ #{self.id} для {self.user.username}"
    class Meta:
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # цена на момент покупки

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# Create your models here.
