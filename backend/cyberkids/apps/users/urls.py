from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'countries', CountryViewSet)
# router.register(r'risk-levels', RiskLevelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
