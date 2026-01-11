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
        """Lista mascotas disponibles para comprar."""
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
    queryset = UserPet.objects.all()
    serializer_class = UserPetSerializer

    def get_queryset(self):
        queryset = UserPet.objects.select_related('pet', 'user')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['post'])
    def buy(self, request):
        """Comprar una mascota con cybercreds."""
        user_id = request.data.get('user_id')
        pet_id = request.data.get('pet_id')

        user = get_object_or_404(CyberUser, pk=user_id)
        pet = get_object_or_404(Pet, pk=pet_id)

        # Verificar si ya tiene la mascota
        if UserPet.objects.filter(user=user, pet=pet).exists():
            return Response({'error': 'Ya tienes esta mascota'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar cybercreds
        if user.cybercreds < pet.cybercreds_cost:
            return Response({'error': 'No tienes suficientes cybercreds'}, status=status.HTTP_400_BAD_REQUEST)

        # Descontar y crear
        user.cybercreds -= pet.cybercreds_cost
        user.save(update_fields=['cybercreds'])

        user_pet = UserPet.objects.create(user=user, pet=pet)
        return Response(UserPetSerializer(user_pet).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def equip(self, request):
        """Equipar una mascota."""
        user_id = request.data.get('user_id')
        pet_id = request.data.get('pet_id')

        user = get_object_or_404(CyberUser, pk=user_id)

        # Desequipar todas las mascotas del usuario
        UserPet.objects.filter(user=user).update(is_equipped=False)

        # Equipar la seleccionada
        user_pet = get_object_or_404(UserPet, user_id=user_id, pet_id=pet_id)
        user_pet.is_equipped = True
        user_pet.save(update_fields=['is_equipped'])

        # Actualizar pet_id en usuario
        user.pet_id = pet_id
        user.save(update_fields=['pet_id'])

        return Response(UserPetSerializer(user_pet).data)

    @action(detail=False, methods=['get'], url_path='equipped/(?P<user_id>[^/.]+)')
    def equipped(self, request, user_id=None):
        """Obtiene la mascota equipada de un usuario."""
        user_pet = UserPet.objects.filter(user_id=user_id, is_equipped=True).first()
        if user_pet:
            return Response(UserPetSerializer(user_pet).data)
        return Response({'error': 'No hay mascota equipada'}, status=status.HTTP_404_NOT_FOUND)
