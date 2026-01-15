from rest_framework import serializers
from .models import CyberUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Preferences
from .models import Country


class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CyberUser
        fields = [
            'user_id', 'username', 'email', 'country',
            'risk_level', 'pet_id', 'cybercreds', 'created_at',
            'last_login', 'is_active', 'avatar', 'preferences'
        ]
        read_only_fields = ['user_id', 'created_at', 'last_login']
    
    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return "https://res.cloudinary.com/dsvynqyq5/image/upload/v1768140305/3dcd4af5bc9e06d36305984730ab7888_o3eeob.jpg"


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


class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer para actualizar datos del usuario"""
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = CyberUser
        fields = ['username', 'email', 'avatar', 'country']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }
    
    def validate_email(self, value):
        user = self.context.get('request').user_instance
        if value and CyberUser.objects.filter(email=value.lower()).exclude(user_id=user.user_id).exists():
            raise serializers.ValidationError('Este email ya está registrado por otro usuario')
        return value.lower() if value else value


class UpdatePreferencesSerializer(serializers.ModelSerializer):
    """Serializer para actualizar preferencias del usuario"""
    class Meta:
        model = Preferences
        fields = ['receive_newsletters', 'dark_mode', 'base_content', 'tone_instructions', 'age']
        extra_kwargs = {
            'receive_newsletters': {'required': False},
            'dark_mode': {'required': False},
            'base_content': {'required': False},
            'tone_instructions': {'required': False},
            'age': {'required': False},
        }


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=6, required=True)
    new_password_confirm = serializers.CharField(write_only=True, min_length=6, required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Las contraseñas no coinciden'})
        return data


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['country_id', 'name', 'iso_code', 'language', 'is_active']
