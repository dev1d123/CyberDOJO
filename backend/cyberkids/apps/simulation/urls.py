from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'scenarios', ScenarioViewSet)
# router.register(r'sensitive-patterns', SensitivePatternViewSet)
# router.register(r'game-sessions', GameSessionViewSet)
# router.register(r'chat-messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
