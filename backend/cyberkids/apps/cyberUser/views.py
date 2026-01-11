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
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, PreferencesSerializer 


def generate_tokens_for_cyberuser(user):
    from datetime import datetime
    from .models import Preferences

    if not user.preferences:
        preferences = Preferences.objects.create()
        user.preferences = preferences
        user.save(update_fields=['preferences'])
    else:
        preferences = user.preferences

    access_payload = {
        'user_id': user.user_id,
        'email': user.email,
        'username': user.username,
        'country': user.country.name if user.country else None,
        'risk_level': user.risk_level.name if user.risk_level else None,
        'cybercreds': user.cybercreds,
        'is_active': user.is_active,
        'avatar': user.avatar.url if user.avatar else None,
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
            'user': UserSerializer(user).data,
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


class MeView(APIView):
    permission_classes = [AllowAny]  # Validamos manualmente el token

    def get(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({'error': 'Token no proporcionado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CyberUser.objects.get(user_id=payload['user_id'], is_active=True)
            return Response(UserSerializer(user).data)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expirado'}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, CyberUser.DoesNotExist):
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)


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
