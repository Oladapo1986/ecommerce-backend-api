from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product, Category, Cart, CartItem, Order

User = get_user_model()


class ProductTests(TestCase):
    """Test product CRUD operations."""

    def setUp(self):
        self.client = APIClient()
        self.product_url = '/api/v1/products/'
        self.category = Category.objects.create(name='Electronics', description='Electronic devices')
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.staff_user = User.objects.create_user(
            username='staffuser', password='testpass123', is_staff=True
        )

    def test_list_products_public(self):
        """Test listing products (public access)."""
        Product.objects.create(
            name='Laptop',
            description='A laptop',
            price=999.99,
            stock_quantity=10,
            category=self.category
        )
        response = self.client.get(self.product_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product_authenticated(self):
        """Test creating product (staff only)."""
        self.client.force_authenticate(user=self.staff_user)
        data = {
            'name': 'Phone',
            'description': 'A smartphone',
            'price': 799.99,
            'stock_quantity': 20,
            'category_id': self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Phone')

    def test_create_product_unauthorized(self):
        """Test creating product without authentication fails."""
        data = {
            'name': 'Phone',
            'description': 'A smartphone',
            'price': 799.99,
            'stock_quantity': 20,
            'category_id': self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_products_by_category(self):
        """Test filtering products by category."""
        product1 = Product.objects.create(
            name='Laptop',
            description='A laptop',
            price=999.99,
            stock_quantity=10,
            category=self.category
        )
        category2 = Category.objects.create(name='Books', description='Books')
        product2 = Product.objects.create(
            name='Django Book',
            description='Learn Django',
            price=29.99,
            stock_quantity=100,
            category=category2
        )
        url = f'{self.product_url}?category={self.category.id}'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')

    def test_search_products(self):
        """Test searching products by name."""
        Product.objects.create(
            name='Laptop Pro',
            description='A professional laptop',
            price=1999.99,
            stock_quantity=5,
            category=self.category
        )
        Product.objects.create(
            name='Desktop Computer',
            description='A desktop',
            price=1299.99,
            stock_quantity=8,
            category=self.category
        )
        url = f'{self.product_url}?search=Laptop'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop Pro')


class CartTests(TestCase):
    """Test cart operations."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A laptop',
            price=999.99,
            stock_quantity=10,
            category=self.category
        )
        self.cart_url = '/api/v1/cart/'
        self.cart_add_url = '/api/v1/cart/add/'
        self.cart_remove_url = '/api/v1/cart/remove/'

    def test_retrieve_cart_authenticated(self):
        """Test retrieving user's cart."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

    def test_retrieve_cart_unauthenticated(self):
        """Test retrieving cart without authentication fails."""
        response = self.client.get(self.cart_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_item_to_cart(self):
        """Test adding item to cart."""
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(self.cart_add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['cartitem_set']), 1)
        self.assertEqual(response.data['cartitem_set'][0]['quantity'], 2)

    def test_add_duplicate_item_to_cart(self):
        """Test adding duplicate item increases quantity."""
        self.client.force_authenticate(user=self.user)
        # Add first time
        data = {'product_id': self.product.id, 'quantity': 2}
        self.client.post(self.cart_add_url, data, format='json')
        # Add again
        data = {'product_id': self.product.id, 'quantity': 1}
        response = self.client.post(self.cart_add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cartitem_set'][0]['quantity'], 3)

    def test_remove_item_from_cart(self):
        """Test removing item from cart."""
        self.client.force_authenticate(user=self.user)
        # Add item
        data = {'product_id': self.product.id, 'quantity': 2}
        self.client.post(self.cart_add_url, data, format='json')
        # Remove entire item
        data = {'product_id': self.product.id}
        response = self.client.post(self.cart_remove_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['cartitem_set']), 0)

    def test_reduce_item_quantity_in_cart(self):
        """Test reducing item quantity in cart."""
        self.client.force_authenticate(user=self.user)
        # Add item with quantity 5
        data = {'product_id': self.product.id, 'quantity': 5}
        self.client.post(self.cart_add_url, data, format='json')
        # Reduce by 2
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(self.cart_remove_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cartitem_set'][0]['quantity'], 3)


class OrderTests(TestCase):
    """Test order operations."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A laptop',
            price=999.99,
            stock_quantity=10,
            category=self.category
        )
        self.checkout_url = '/api/v1/checkout/'
        self.orders_url = '/api/v1/orders/'

    def test_checkout_success(self):
        """Test successful checkout."""
        self.client.force_authenticate(user=self.user)
        # Add item to cart
        data = {'product_id': self.product.id, 'quantity': 2}
        self.client.post('/api/v1/cart/add/', data, format='json')
        # Checkout
        response = self.client.post(self.checkout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_price'], '1999.99')
        self.assertEqual(response.data['status'], 'Paid')

    def test_checkout_empty_cart(self):
        """Test checkout with empty cart fails."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.checkout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_insufficient_stock(self):
        """Test checkout with insufficient stock fails."""
        self.client.force_authenticate(user=self.user)
        # Try to add more than available stock
        data = {'product_id': self.product.id, 'quantity': 20}
        self.client.post('/api/v1/cart/add/', data, format='json')
        response = self.client.post(self.checkout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user_orders(self):
        """Test listing user's orders."""
        self.client.force_authenticate(user=self.user)
        # Create an order
        order = Order.objects.create(user=self.user, total_price=999.99, status='Paid')
        response = self.client.get(self.orders_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], order.id)

    def test_list_orders_only_user_orders(self):
        """Test that users only see their own orders."""
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        # Create orders for both users
        order1 = Order.objects.create(user=self.user, total_price=999.99, status='Paid')
        order2 = Order.objects.create(user=other_user, total_price=499.99, status='Pending')
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.orders_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], order1.id)
