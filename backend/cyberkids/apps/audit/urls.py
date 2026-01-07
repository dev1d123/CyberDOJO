from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'activity-logs', ActivityLogViewSet)
# router.register(r'sessions', UserSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
