from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('api/accounts/', include('accounts.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/cars/', include('cars.urls')),
    path('api/rentals/', include('rentals.urls')),
    path('metrics/', lambda request: HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)),
]
