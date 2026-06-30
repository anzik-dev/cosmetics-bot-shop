from django.contrib import admin
from .models import Order, OrderItem
from .models import Product, ProductImage
from .models import Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 10

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)




@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'product', 'created_at')

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = "Пользователь"

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # не добавлять пустые строки
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False  # если нужно запретить удалять товары из админки

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'address__address', 'id')
    readonly_fields = ('total', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

# Register your models here.
