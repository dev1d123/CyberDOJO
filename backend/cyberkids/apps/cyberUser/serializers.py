from rest_framework import serializers
from .models import CyberUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyberUser
        fields = [
            'user_id', 'username', 'email', 'country',
            'risk_level', 'pet_id', 'cybercreds', 'created_at',
            'last_login', 'is_active'
        ]
        read_only_fields = ['user_id', 'created_at', 'last_login']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CyberUser
        fields = ['username', 'email', 'password', 'password_confirm', 'country']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden'})
        if CyberUser.objects.filter(email=data['email'].lower()).exists():
            raise serializers.ValidationError({'email': 'Este email ya está registrado'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CyberUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
