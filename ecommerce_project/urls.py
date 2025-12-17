from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line includes your app's URLs
    path('api/v1/', include('core_api.urls')), 
]
