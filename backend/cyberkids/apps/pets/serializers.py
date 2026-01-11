from rest_framework import serializers
from .models import Pet, PetState, UserPet


class PetStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetState
        fields = '__all__'


class PetSerializer(serializers.ModelSerializer):
    states = PetStateSerializer(many=True, read_only=True)

    class Meta:
        model = Pet
        fields = '__all__'


class UserPetSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)

    class Meta:
        model = UserPet
        fields = '__all__'
