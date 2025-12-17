# core_api/views.py

from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Product, Cart, CartItem, Order, OrderItem, Category
from .serializers import ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer, RegisterSerializer, CategorySerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for categories (list and retrieve)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    # What data should this view work with? All products.
    queryset = Product.objects.all().order_by('name')
    # What serializer should be used to format the data?
    serializer_class = ProductSerializer
    # Later, we will add permissions here to restrict POST/PUT/DELETE

# ADD THIS LINE:
    # Allows GET (read) for anyone, but requires staff status for POST/PUT/DELETE (write)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # Enable filtering, searching, and ordering
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']
    
    # ----------------------------------------------------
# 1. Cart Retrieve View (GET)
# ----------------------------------------------------

class CartRetrieveView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    # Only authenticated users can view their cart
    permission_classes = [permissions.IsAuthenticated]

    # This function ensures the user only gets *their* cart
    def get_object(self):
        user = self.request.user
        # Get the cart if it exists, otherwise create it
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

# ----------------------------------------------------
# 2. Add/Update Item View (POST)
# ----------------------------------------------------

class CartAddItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # We expect product_id and quantity from the request body
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1) 

        # 1. Get the authenticated user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # 2. Check if the product exists
        product = get_object_or_404(Product, id=product_id)

        # Validate that quantity is a positive integer
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({"detail": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Check if the item is already in the cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            # If the item already exists, only update the quantity field
            defaults={'quantity': quantity}
        )
        
        # If the item was not created (it already existed), update its quantity
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

class CartRemoveItemView(APIView):
    """Remove an item from the cart or reduce its quantity."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # We expect product_id and optional quantity from the request body
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')  # If not provided, remove entire item

        # 1. Get the authenticated user's cart
        cart = get_object_or_404(Cart, user=request.user)
        
        # 2. Check if the item exists in the cart
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        # 3. Remove or reduce quantity
        if quantity is None:
            # Remove entire item
            cart_item.delete()
        else:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    cart_item.delete()
                elif quantity >= cart_item.quantity:
                    cart_item.delete()
                else:
                    cart_item.quantity -= quantity
                    cart_item.save()
            except (ValueError, TypeError):
                return Response({"detail": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    """
    Handles the checkout process for authenticated users by validating cart items,
    checking product stock, creating an order and order items, updating product stock,
    and clearing the cart upon successful checkout.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.cartitem_set.all()

        if not cart_items:
            raise ValidationError({"detail": "Cannot checkout an empty cart."})

        total_price = Decimal('0.00')
        order_items_to_create = []

        # 1. Validation and Stock Check
        for item in cart_items:
            if item.product.stock_quantity < item.quantity:
                raise ValidationError({
                    "detail": f"Not enough stock for {item.product.name}. Available: {item.product.stock_quantity}"
                })
            
            # Calculate running total using Decimal for precision
            item_total = Decimal(str(item.quantity)) * Decimal(str(item.product.price))
            total_price += item_total
        
        # 2. Create the Order
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            status='Paid' # Mocked as paid instantly for simplicity
        )

        # 3. Create Order Items and Update Stock
        for item in cart_items:
            # Prepare OrderItem
            order_items_to_create.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price # Save the current price
            ))
            
            # Update Product Stock
            item.product.stock_quantity -= item.quantity
            if item.product.stock_quantity < 0:
                raise ValidationError({
                    "detail": f"Stock for {item.product.name} cannot be negative after update."
                })
        
        # 4. Create the OrderItems in bulk
        OrderItem.objects.bulk_create(order_items_to_create)
        
        # 5. Update product stock for all items
        for item in cart_items:
            item.product.save()
        
        # 6. Clear the Cart (Last step, done only if everything succeeds)
        CartItem.objects.filter(cart=cart).delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """Lists orders belonging to the authenticated user."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return orders for the requesting user
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update order details (user-scoped)."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Only return orders for the requesting user
        return Order.objects.filter(user=self.request.user)


class RegisterView(APIView):
    """Simple user registration endpoint."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)