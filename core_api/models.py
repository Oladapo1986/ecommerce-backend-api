from django.db import models
from django.contrib.auth.models import User # <-- Import the User model

# -----------------
# Category Model
# -----------------
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

# I am creating my model below
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # DecimalField is best for money to avoid rounding errors
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    def __str__(self):
        return self.name
    
    # -----------------
# Cart Model: This indicates One-to-one with User
# -----------------
class Cart(models.Model):
    # Here, the code will trigger deletion of the cart if the user is deleted
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

# -----------------
# CartItem Model: This model helps to store what and how much is in the cart
# -----------------
class CartItem(models.Model):
    # If the cart is deleted, the item is deleted
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE) 
    # If the product is deleted, the item is deleted
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    # Here, I'm adding a property to calculate item total price
    @property
    def total_price(self):
        return self.quantity * self.product.price
    
    # core_api/models.py (ensure these models are present)

# -----------------
# The code below shows the order Model
# -----------------
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

# -----------------
# OrderItem Model: Details of items *in* the order
# -----------------
class OrderItem(models.Model):
    """
    Represents an item within an order.
    The price_at_purchase field is critical for historical accuracy, ensuring that the price paid for each product at the time of purchase is recorded,
    even if the product price changes later or the product is deleted.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # Link to Product, but set to null if product is deleted (don't delete the order)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    # The is CRITICAL: Store the price at the time of purchase
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"
