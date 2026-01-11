from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet, PetStateViewSet, UserPetViewSet

router = DefaultRouter()
router.register(r'pets', PetViewSet, basename='pets')
router.register(r'states', PetStateViewSet, basename='pet-states')
router.register(r'user-pets', UserPetViewSet, basename='user-pets')
urlpatterns = [
    path('', include(router.urls)),
]