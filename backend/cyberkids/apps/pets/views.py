from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Pet, PetState, UserPet
from .serializers import PetSerializer, PetStateSerializer, UserPetSerializer
from apps.cyberUser.models import CyberUser


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.prefetch_related('states').all()
    serializer_class = PetSerializer

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Obtiene la mascota por defecto."""
        pet = Pet.objects.filter(is_default=True).first()
        if pet:
            return Response(PetSerializer(pet).data)
        return Response({'error': 'No hay mascota por defecto'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def shop(self, request):
        """Lista mascotas disponibles para comprar.
        NOTA: Para comprar mascotas, usa el endpoint /api/progression/shop/buy-pet/
        """
        pets = Pet.objects.filter(is_default=False)
        return Response(PetSerializer(pets, many=True).data)


class PetStateViewSet(viewsets.ModelViewSet):
    queryset = PetState.objects.all()
    serializer_class = PetStateSerializer

    def get_queryset(self):
        queryset = PetState.objects.all()
        pet_id = self.request.query_params.get('pet_id')
        if pet_id:
            queryset = queryset.filter(pet_id=pet_id)
        return queryset


class UserPetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las mascotas del usuario.
    NOTA: Para comprar mascotas, usa /api/progression/shop/buy-pet/
    """
    queryset = UserPet.objects.all()
    serializer_class = UserPetSerializer

    def get_queryset(self):
        queryset = UserPet.objects.select_related('pet', 'user')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='equipped/(?P<user_id>[^/.]+)')
    def equipped(self, request, user_id=None):
        """Obtiene la mascota equipada de un usuario."""
        user_pet = UserPet.objects.filter(user_id=user_id, is_equipped=True).first()
        if user_pet:
            return Response(UserPetSerializer(user_pet).data)
        return Response({'error': 'No hay mascota equipada'}, status=status.HTTP_404_NOT_FOUND)
