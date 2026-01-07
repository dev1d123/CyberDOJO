from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'questions', OnboardingQuestionViewSet)
# router.register(r'options', AnswerOptionViewSet)
# router.register(r'responses', OnboardingResponseViewSet)
# router.register(r'user-stats', UserStatisticViewSet)
# router.register(r'global-stats', GlobalStatisticViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
