from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MinigameViewSet, SwipeQuestionViewSet, MinigameSessionViewSet, SwipeResponseViewSet

router = DefaultRouter()
router.register(r'games', MinigameViewSet, basename='minigames')
router.register(r'questions', SwipeQuestionViewSet, basename='swipe-questions')
router.register(r'sessions', MinigameSessionViewSet, basename='minigame-sessions')
router.register(r'responses', SwipeResponseViewSet, basename='swipe-responses')
urlpatterns = [
    path('', include(router.urls)),
]
