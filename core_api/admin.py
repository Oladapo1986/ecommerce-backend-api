from django.contrib import admin
from .models import Product, Cart, CartItem, Category, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active']
    search_fields = ['name', 'description']
    list_filter = ['category', 'is_active', 'created_at']

admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    search_fields = ['user__username']
    list_filter = ['status', 'created_at']
    readonly_fields = ['total_price', 'created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price_at_purchase']
    search_fields = ['product__name', 'order__id']