from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import jwt
from .models import CyberUser, Country
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, PreferencesSerializer,
    UpdateUserSerializer, UpdatePreferencesSerializer, ChangePasswordSerializer
    , CountrySerializer
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


# NOTA: get_user_from_token ya no es necesaria. 
# Usa IsAuthenticated como permission_class y request.user será el CyberUser autenticado.


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user ya es CyberUser gracias a JWTCustomAuthentication
        return Response(UserSerializer(request.user).data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request):
        # request.user ya es CyberUser gracias a JWTCustomAuthentication
        user = request.user
        
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user ya es CyberUser gracias a JWTCustomAuthentication
        user = request.user
        
        if not user.preferences:
            from .models import Preferences
            preferences = Preferences.objects.create()
            user.preferences = preferences
            user.save(update_fields=['preferences'])
        
        return Response(PreferencesSerializer(user.preferences).data)

    def patch(self, request):
        # request.user ya es CyberUser gracias a JWTCustomAuthentication
        user = request.user
        
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # request.user ya es CyberUser gracias a JWTCustomAuthentication
        user = request.user
        
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


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoints for countries"""
    queryset = Country.objects.filter(is_active=True).order_by('name')
    serializer_class = CountrySerializer
    lookup_field = 'country_id'


class DashboardView(APIView):
    """
    Dashboard del usuario con resumen completo de su progreso y estado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Importar modelos necesarios
        from apps.progression.models import UserProgress, CreditTransaction, UserInventory
        from apps.pets.models import UserPet
        from apps.simulation.models import GameSession
        from apps.minigames.models import MinigameSession
        from apps.onboarding.models import OnboardingQuestion, OnboardingResponse
        
        # Progreso del usuario
        progress = UserProgress.objects.filter(user=user).select_related('current_level').first()
        
        # Estadísticas de simulación
        simulation_sessions = GameSession.objects.filter(user=user)
        simulation_stats = {
            'total_sessions': simulation_sessions.count(),
            'won': simulation_sessions.filter(outcome='won').count(),
            'lost': simulation_sessions.filter(outcome='failed').count(),
            'in_progress': simulation_sessions.filter(is_game_over__isnull=True).count(),
        }
        
        # Estadísticas de minijuegos
        minigame_sessions = MinigameSession.objects.filter(user=user)
        minigame_stats = {
            'total_sessions': minigame_sessions.count(),
            'total_points': sum(s.points_earned or 0 for s in minigame_sessions),
            'total_correct': sum(s.correct_answers or 0 for s in minigame_sessions),
        }
        
        # Estado del onboarding
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        answered_questions = OnboardingResponse.objects.filter(user=user).count()
        onboarding_complete = answered_questions >= total_questions if total_questions > 0 else False
        
        # Mascotas y cosméticos
        pets_owned = UserPet.objects.filter(user=user).count()
        equipped_pet = UserPet.objects.filter(user=user, is_equipped=True).select_related('pet').first()
        cosmetics_owned = UserInventory.objects.filter(user=user).count()
        
        # Últimas transacciones
        recent_transactions = CreditTransaction.objects.filter(user=user).order_by('-created_at')[:5]
        
        return Response({
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'cybercreds': user.cybercreds,
                'risk_level': user.risk_level.name if user.risk_level else None,
                'country': user.country.name if user.country else None,
            },
            'progress': {
                'current_level': progress.current_level.level_number if progress and progress.current_level else 1,
                'level_name': progress.current_level.name if progress and progress.current_level else 'Principiante',
                'current_xp': progress.current_xp if progress else 0,
                'games_played': progress.games_played if progress else 0,
                'games_won': progress.games_won if progress else 0,
            },
            'simulation': simulation_stats,
            'minigames': minigame_stats,
            'onboarding': {
                'is_complete': onboarding_complete,
                'progress': f'{answered_questions}/{total_questions}',
                'percentage': round((answered_questions / total_questions * 100) if total_questions > 0 else 0, 1)
            },
            'inventory': {
                'pets_owned': pets_owned,
                'equipped_pet': equipped_pet.pet.name if equipped_pet else None,
                'cosmetics_owned': cosmetics_owned,
            },
            'recent_transactions': [
                {
                    'amount': t.amount,
                    'type': t.transaction_type,
                    'description': t.description,
                    'date': t.created_at.isoformat()
                } for t in recent_transactions
            ]
        })
