from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'slangs', SlangViewSet)
# router.register(r'prompt-templates', SystemPromptTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
