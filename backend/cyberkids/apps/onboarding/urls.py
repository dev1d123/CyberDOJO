from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OnboardingQuestionViewSet,
    AnswerOptionViewSet,
    OnboardingResponseViewSet,
    UserStatisticViewSet,
    GlobalStatisticViewSet
)

router = DefaultRouter()
router.register(r'questions', OnboardingQuestionViewSet, basename='onboarding-questions')
router.register(r'options', AnswerOptionViewSet, basename='answer-options')
router.register(r'responses', OnboardingResponseViewSet, basename='onboarding-responses')
router.register(r'user-stats', UserStatisticViewSet, basename='user-statistics')
router.register(r'global-stats', GlobalStatisticViewSet, basename='global-statistics')

urlpatterns = [
    path('', include(router.urls)),
]
