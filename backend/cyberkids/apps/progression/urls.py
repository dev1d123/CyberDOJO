from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgressionLevelViewSet, CosmeticItemViewSet,
    UserInventoryViewSet, CreditTransactionViewSet, UserProgressViewSet,
    ShopViewSet, AchievementViewSet, UserAchievementViewSet
)

router = DefaultRouter()
router.register(r'levels', ProgressionLevelViewSet, basename='progression-levels')
router.register(r'cosmetics', CosmeticItemViewSet, basename='cosmetic-items')
router.register(r'inventory', UserInventoryViewSet, basename='user-inventory')
router.register(r'transactions', CreditTransactionViewSet, basename='credit-transactions')
router.register(r'progress', UserProgressViewSet, basename='user-progress')
router.register(r'shop', ShopViewSet, basename='shop')
router.register(r'achievements', AchievementViewSet, basename='achievements')
router.register(r'user-achievements', UserAchievementViewSet, basename='user-achievements')

urlpatterns = [
    path('', include(router.urls)),
]
