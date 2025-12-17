# Ecommerce API

A production-ready ecommerce REST API built with Django and Django REST Framework (DRF). This project demonstrates core backend development concepts including user authentication with JWT, product management, shopping carts, and orders with role-based access control.

## Features

### Core Functionality
- **User Authentication**: JWT-based authentication with registration and login endpoints
- **Product Management**: Create, read, update, delete products with categories
- **Categories**: Organize products by category
- **Shopping Cart**: Add/remove items, manage quantities per user
- **Orders**: Checkout from cart, order history, order status tracking
- **Permissions**: Role-based access (admin vs regular users)

### Professional-Level Features
- **Filtering & Search**: Filter products by category, search by name/description
- **Pagination**: Page-based pagination (10 items per page)
- **Stock Management**: Track inventory, validate stock during checkout
- **Environment Variables**: Secure configuration with `.env` files
- **Unit Tests**: Comprehensive test suite covering auth, products, cart, and orders
- **Admin Interface**: Fully configured Django admin with search and filters

##  Quick Start

### Prerequisites
- Python 3.10+
- pip or conda
- Git

### Installation

1. **Clone the repository** (if applicable):
```bash
cd ecommerce_api_portfolio
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Create `.env` file** (copy from `.env.example`):
```bash
cp .env.example .env
```
Edit `.env` and set a secure `SECRET_KEY` for production.

5. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser** (for admin access):
```bash
python manage.py createsuperuser
```

7. **Run development server**:
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/v1/`

##  Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
DEBUG=True                          # Set to False in production
SECRET_KEY=your-secure-key-here     # Generate a secure key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# JWT Settings (in minutes/days)
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

##  API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/token/` | Obtain access & refresh tokens |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/` | List products (paginated) |
| GET | `/api/v1/products/?category=1&search=laptop&ordering=-price` | Filter & search products |
| POST | `/api/v1/products/` | Create product (staff only) |
| GET | `/api/v1/products/{id}/` | Get product details |
| PUT | `/api/v1/products/{id}/` | Update product (staff only) |
| DELETE | `/api/v1/products/{id}/` | Delete product (staff only) |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories/` | List all categories |
| POST | `/api/v1/categories/` | Create category (staff only) |
| GET | `/api/v1/categories/{id}/` | Get category details |

### Shopping Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cart/` | Get user's cart |
| POST | `/api/v1/cart/add/` | Add item to cart |
| POST | `/api/v1/cart/remove/` | Remove or reduce item quantity |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/checkout/` | Create order from cart |
| GET | `/api/v1/orders/` | List user's orders |
| GET | `/api/v1/orders/{id}/` | Get order details |
| PUT | `/api/v1/orders/{id}/` | Update order (e.g., status) |

##  Authentication

All endpoints except `/api/v1/auth/register/`, `/api/v1/products/` (GET), and `/api/v1/categories/` (GET) require authentication.

### Example: Register and Login

1. **Register**:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "strongpass123"
  }'
```

2. **Obtain Tokens**:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "strongpass123"
  }'
```

Response:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

3. **Use Access Token**:
```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://127.0.0.1:8000/api/v1/cart/
```

##  Example Workflow

### 1. View Products
```bash
curl http://127.0.0.1:8000/api/v1/products/
```

### 2. Add Item to Cart
```bash
curl -X POST http://127.0.0.1:8000/api/v1/cart/add/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### 3. View Cart
```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://127.0.0.1:8000/api/v1/cart/
```

### 4. Checkout
```bash
curl -X POST http://127.0.0.1:8000/api/v1/checkout/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 5. View Orders
```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://127.0.0.1:8000/api/v1/orders/
```

##  Running Tests

Run all tests:
```bash
python manage.py test
```

Run specific test file:
```bash
python manage.py test core_api.test_auth
python manage.py test core_api.test_api
```

Run with coverage:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

##  Admin Dashboard

Access the Django admin at `http://127.0.0.1:8000/admin/`

Login with your superuser credentials. You can:
- Manage products and categories
- View and update orders
- Search and filter data
- Create/modify users

##  Project Structure

```
ecommerce_api_portfolio/
├── manage.py
├── db.sqlite3
├── .env.example
├── requirements.txt
├── core_api/
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin configuration
│   ├── test_auth.py           # Authentication tests
│   ├── test_api.py            # API tests
│   └── migrations/
├── ecommerce_project/
│   ├── settings.py            # Django settings
│   ├── urls.py                # Project URLs
│   ├── asgi.py
│   └── wsgi.py
└── venv/                      # Virtual environment
```

##  Technologies Used

- **Django 5.2** - Web framework
- **Django REST Framework** - REST API toolkit
- **djangorestframework-simplejwt** - JWT authentication
- **django-filter** - Filtering and search
- **python-decouple** - Environment configuration
- **SQLite** - Development database

##  API Response Format

### Success Response (200)
```json
{
  "id": 1,
  "name": "Laptop",
  "price": "999.99",
  "stock_quantity": 10,
  "category": {
    "id": 1,
    "name": "Electronics"
  }
}
```

### Error Response (400/401)
```json
{
  "detail": "Invalid request",
  "error_code": "VALIDATION_ERROR"
}
```

##  Security Notes

- **Never commit `.env` files** with real secrets to version control
- Use strong `SECRET_KEY` in production (generate with Django `get_random_secret_key()`)
- Set `DEBUG=False` in production
- Use HTTPS in production
- Implement CORS if frontend is on different domain
- Add rate limiting for API endpoints
- Use database migrations for schema changes

##  Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`
3. Set `ALLOWED_HOSTS` to your domain(s)
4. Use PostgreSQL instead of SQLite
5. Collect static files: `python manage.py collectstatic`
6. Use Gunicorn/uWSGI as application server
7. Configure Nginx as reverse proxy
8. Set up SSL certificate

##  Additional Resources

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [JWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)

##  License

This project is open source and available under the MIT License.

## 👤 Author

Created as a portfolio project for backend development. To contact the developer, send a message to oladapo.oluseye@gmail.com

---

**Need help?** Check the test files for example API usage or open an issue!
