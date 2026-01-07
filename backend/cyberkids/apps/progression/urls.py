from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'levels', ProgressionLevelViewSet)
# router.register(r'cosmetics', CosmeticItemViewSet)
# router.register(r'inventory', UserInventoryViewSet)
# router.register(r'transactions', CreditTransactionViewSet)
# router.register(r'progress', UserProgressViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
