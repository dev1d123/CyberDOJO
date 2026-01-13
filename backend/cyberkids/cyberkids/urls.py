from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="CyberKids API",
        default_version='v1',
        description="API para la plataforma educativa CyberKids - Ciberseguridad para niños",
        terms_of_service="https://www.cyberkids.com/terms/",
        contact=openapi.Contact(email="contact@cyberkids.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Documentación API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API routes
    path('api/users/', include('apps.cyberUser.urls')),
    path('api/simulation/', include('apps.simulation.urls')),
    path('api/pets/', include('apps.pets.urls')),
    path('api/minigames/', include('apps.minigames.urls')),
    path('api/progression/', include('apps.progression.urls')),
    path('api/onboarding/', include('apps.onboarding.urls')),
    path('api/audit/', include('apps.audit.urls')),
    path('api/llm/', include('apps.llm.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)