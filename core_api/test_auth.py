from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class RegistrationTests(TestCase):
    """Test user registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'

    def test_register_user_success(self):
        """Test successful user registration."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_register_user_weak_password(self):
        """Test registration with weak password."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        User.objects.create_user(username='testuser', email='old@example.com', password='pass123')
        data = {
            'username': 'testuser',
            'email': 'new@example.com',
            'password': 'strongpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenObtainTests(TestCase):
    """Test JWT token obtain endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.token_url = '/api/v1/auth/token/'
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_obtain_token_success(self):
        """Test successful token obtain."""
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_wrong_password(self):
        """Test token obtain with wrong password."""
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
