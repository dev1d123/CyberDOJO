from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# TODO: Register viewsets
router.register(r'game-sessions', views.GameSessionViewSet)
router.register(r'chat-messages', views.ChatMessageViewSet)
# Optionally register Scenario and SensitivePattern viewsets later

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.chat, name='simulation-chat'),
    path('session/start-role/', views.start_with_role, name='simulation-start-with-role'),
    path('session/resume/', views.resume_session, name='simulation-resume-session'),
    path('session/<int:session_id>/messages/', views.session_messages, name='simulation-session-messages'),
]
