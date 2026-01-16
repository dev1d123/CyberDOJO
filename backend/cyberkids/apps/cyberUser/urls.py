from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RegisterView, LoginView, MeView, RefreshTokenView,
    UpdateProfileView, UpdatePreferencesView, ChangePasswordView,
    CountryViewSet, DashboardView
)

router = DefaultRouter()
router.register(r'', UserViewSet)
router.register(r'countries', CountryViewSet, basename='country')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/me/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('auth/me/preferences/', UpdatePreferencesView.as_view(), name='update_preferences'),
    path('auth/me/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
