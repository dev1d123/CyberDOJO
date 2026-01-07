from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/users/', include('apps.users.urls')),
    path('api/slang/', include('apps.slang_engine.urls')),
    path('api/simulation/', include('apps.simulation.urls')),
    path('api/pets/', include('apps.pets.urls')),
    path('api/minigames/', include('apps.minigames.urls')),
    path('api/progression/', include('apps.progression.urls')),
    path('api/onboarding/', include('apps.onboarding.urls')),
    path('api/audit/', include('apps.audit.urls')),
]
