"""
URL configuration for ara project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from . import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app import views
    2. Add a URL to urlpatterns:  path('', views.MyView.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('api-auth/', include('rest_framework.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import obtain_auth_token

# API Documentation (Optional: if you want Swagger/OpenAPI docs)
try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False


urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('core.urls')),
    path('api/auth/', include('accounts.urls')),
    
    # REST Framework authentication
    path('api-auth/', include('rest_framework.urls')),
    
    # Token authentication endpoint
    path('api/auth/token/', obtain_auth_token, name='api-token-auth'),
]

# Add API documentation if available (Optional)
if SPECTACULAR_AVAILABLE:
    urlpatterns += [
        # API Schema
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        
        # Swagger UI
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        
        # ReDoc
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
