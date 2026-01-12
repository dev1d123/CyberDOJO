from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import jwt
from .models import CyberUser
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, PreferencesSerializer,
    UpdateUserSerializer, UpdatePreferencesSerializer, ChangePasswordSerializer
) 


def generate_tokens_for_cyberuser(user):
    from datetime import datetime
    from .models import Preferences

    if not user.preferences:
        preferences = Preferences.objects.create()
        user.preferences = preferences
        user.save(update_fields=['preferences'])
    else:
        preferences = user.preferences

    avatar_url = None
    if user.avatar:
        if hasattr(user.avatar, 'url'):
            avatar_url = user.avatar.url
        else:
            avatar_url = str(user.avatar)

    access_payload = {
        'user_id': user.user_id,
        'email': user.email,
        'username': user.username,
        'country': user.country.name if user.country else None,
        'risk_level': user.risk_level.name if user.risk_level else None,
        'cybercreds': user.cybercreds,
        'is_active': user.is_active,
        'avatar': avatar_url,
        'preferences': {
            'receive_newsletters': preferences.receive_newsletters,
            'dark_mode': preferences.dark_mode,
        },
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'token_type': 'access'
    }

    refresh_payload = {
        **access_payload,
        'exp': datetime.utcnow() + timedelta(days=7),
        'token_type': 'refresh'
    }

    return {
        'access': jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256'),
        'refresh': jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256'),
    }




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        tokens = generate_tokens_for_cyberuser(user)
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            #'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        
        try:
            user = CyberUser.objects.get(email=email, is_active=True)
        except CyberUser.DoesNotExist:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.check_password(password):
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        tokens = generate_tokens_for_cyberuser(user)
        
        return Response({
            'message': 'Login exitoso',
            # 'user': UserSerializer(user).data,
            'tokens': tokens
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            if payload.get('token_type') != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')
            
            user = CyberUser.objects.get(user_id=payload['user_id'], is_active=True)
            tokens = generate_tokens_for_cyberuser(user)
            
            return Response({'tokens': tokens})
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expirado'}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, CyberUser.DoesNotExist):
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)


def get_user_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, Response({'error': 'Token no proporcionado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = CyberUser.objects.get(user_id=payload['user_id'], is_active=True)
        return user, None
    except jwt.ExpiredSignatureError:
        return None, Response({'error': 'Token expirado'}, status=status.HTTP_401_UNAUTHORIZED)
    except (jwt.InvalidTokenError, CyberUser.DoesNotExist):
        return None, Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [AllowAny]  # Validamos manualmente el token

    def get(self, request):
        user, error_response = get_user_from_token(request)
        if error_response:
            return error_response
        return Response(UserSerializer(user).data)


class UpdateProfileView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request):
        user, error_response = get_user_from_token(request)
        if error_response:
            return error_response
        
        serializer = UpdateUserSerializer(
            user, 
            data=request.data, 
            partial=True,
            context={'request': type('Request', (), {'user_instance': user})()}
        )
        
        if serializer.is_valid():
            serializer.save()
            tokens = generate_tokens_for_cyberuser(user)
            return Response({
                'message': 'Perfil actualizado exitosamente',
                'user': UserSerializer(user).data,
                'tokens': tokens
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class UpdatePreferencesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user, error_response = get_user_from_token(request)
        if error_response:
            return error_response
        
        if not user.preferences:
            from .models import Preferences
            preferences = Preferences.objects.create()
            user.preferences = preferences
            user.save(update_fields=['preferences'])
        
        return Response(PreferencesSerializer(user.preferences).data)

    def patch(self, request):
        user, error_response = get_user_from_token(request)
        if error_response:
            return error_response
        
        # Crear preferencias si no existen
        if not user.preferences:
            from .models import Preferences
            preferences = Preferences.objects.create()
            user.preferences = preferences
            user.save(update_fields=['preferences'])
        
        serializer = UpdatePreferencesSerializer(
            user.preferences, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            # Regenerar tokens con preferencias actualizadas
            tokens = generate_tokens_for_cyberuser(user)
            return Response({
                'message': 'Preferencias actualizadas exitosamente',
                'preferences': PreferencesSerializer(user.preferences).data,
                'tokens': tokens
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user, error_response = get_user_from_token(request)
        if error_response:
            return error_response
        
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verificar contraseña actual
            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {'error': 'La contraseña actual es incorrecta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Establecer nueva contraseña
            user.set_password(serializer.validated_data['new_password'])
            user.save(update_fields=['password'])
            
            # Regenerar tokens
            tokens = generate_tokens_for_cyberuser(user)
            
            return Response({
                'message': 'Contraseña actualizada exitosamente',
                'tokens': tokens
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CyberUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    permission_classes = [AllowAny]  # TODO: Agregar autenticación personalizada

    @action(detail=True, methods=['post'])
    def add_cybercreds(self, request, user_id=None):
        user = self.get_object()
        amount = request.data.get('amount', 0)
        user.cybercreds += int(amount)
        user.save(update_fields=['cybercreds'])
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, user_id=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'message': 'Usuario desactivado'})
