# core_api/serializers.py

from rest_framework import serializers
from .models import Product, Order, OrderItem, Cart, CartItem, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Product
        # '__all__' means include all fields from the Product model,
        # including any fields that are added to the model in the future.
        fields = ['id', 'name', 'description', 'price', 'stock_quantity', 'is_active', 'category', 'category_id', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    # Show product details in the cart
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    # I am Nesting the CartItems inside the Cart
    cartitem_set = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cartitem_set', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    # The Read-only field aid to show the product name
    product_name = serializers.ReadOnlyField(source='product.name') 

    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
    # Nest the OrderItems inside the Orde r
    # If you have set a custom related_name in the OrderItem model's ForeignKey to Order, update 'orderitem_set' below.
    # For example, if related_name='items', use source='items' instead.
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = ['id', 'username', 'items', 'total_price', 'status', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )
        return user
