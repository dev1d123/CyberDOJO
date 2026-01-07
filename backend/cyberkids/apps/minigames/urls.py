from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'minigames', MinigameViewSet)
# router.register(r'swipe-questions', SwipeQuestionViewSet)
# router.register(r'minigame-sessions', MinigameSessionViewSet)
# router.register(r'swipe-responses', SwipeResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
