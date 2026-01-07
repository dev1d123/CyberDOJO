from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Register viewsets
# router.register(r'pets', PetViewSet)
# router.register(r'pet-states', PetStateViewSet)
# router.register(r'user-pets', UserPetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
