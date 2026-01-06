# core_api/urls.py

from rest_framework.routers import DefaultRouter
from rest_framework import generics, permissions
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProductViewSet,
    CartRetrieveView,
    CartAddItemView,
    CartRemoveItemView,
    CheckoutView,
    OrderListView,
    OrderDetailView,
    RegisterView,
    CategoryViewSet,
)
from .models import Order
from .serializers import OrderSerializer

# I first create an instance of the router
router = DefaultRouter()

# The I register the ProductViewSet:
# By passing the first argument 'products' it creates the '/products/' path
router.register(r'products', ProductViewSet)

# The CategoryViewSet is registerd:
# The first argument 'categories' is what creates the '/categories/' path
router.register(r'categories', CategoryViewSet)

# Here, we need to define custom URL patterns for cart operations such as cart URLs, etc
urlpatterns = [
    # Cart URLs
    path('cart/', CartRetrieveView.as_view(), name='cart-retrieve'),
    path('cart/add/', CartAddItemView.as_view(), name='cart-add-item'),
    path('cart/remove/', CartRemoveItemView.as_view(), name='cart-remove-item'),
    
    # Order URLs
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),

    # Authentication / registration
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Append router URLs
urlpatterns += router.urls
