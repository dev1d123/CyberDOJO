from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import OnboardingQuestion, AnswerOption, OnboardingResponse, UserStatistic, GlobalStatistic
from .serializers import (
    OnboardingQuestionSerializer,
    AnswerOptionSerializer,
    OnboardingResponseSerializer,
    UserStatisticSerializer,
    GlobalStatisticSerializer
)
from apps.cyberUser.models import CyberUser, RiskLevel


class OnboardingQuestionViewSet(viewsets.ModelViewSet):
    queryset = OnboardingQuestion.objects.prefetch_related('options').order_by('display_order')
    serializer_class = OnboardingQuestionSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lista todas las preguntas activas del onboarding."""
        questions = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)


class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = AnswerOption.objects.all()
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        return queryset


class OnboardingResponseViewSet(viewsets.ModelViewSet):
    queryset = OnboardingResponse.objects.all()
    serializer_class = OnboardingResponseSerializer

    def get_queryset(self):
        queryset = OnboardingResponse.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request):
        """Enviar una respuesta individual para el usuario autenticado."""
        user = request.user
        question_id = request.data.get('question_id')
        option_id = request.data.get('option_id')
        
        if not question_id:
            return Response({'error': 'question_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        question = get_object_or_404(OnboardingQuestion, pk=question_id)
        option = get_object_or_404(AnswerOption, pk=option_id) if option_id else None
        
        # Crear o actualizar respuesta
        response, created = OnboardingResponse.objects.update_or_create(
            user=user,
            question=question,
            defaults={'option': option}
        )
        
        return Response({
            'response': OnboardingResponseSerializer(response).data,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='submit-batch', permission_classes=[IsAuthenticated])
    def submit_batch(self, request):
        """Enviar múltiples respuestas en lote para el usuario autenticado."""
        user = request.user
        responses_data = request.data.get('responses', [])
        
        if not responses_data:
            return Response({'error': 'Se requiere un array de responses'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_responses = []
        updated_responses = []
        
        for item in responses_data:
            question_id = item.get('question_id')
            option_id = item.get('option_id')
            
            if not question_id:
                continue
                
            try:
                question = OnboardingQuestion.objects.get(pk=question_id)
                option = AnswerOption.objects.get(pk=option_id) if option_id else None
                
                response, created = OnboardingResponse.objects.update_or_create(
                    user=user,
                    question=question,
                    defaults={'option': option}
                )
                
                if created:
                    created_responses.append(response)
                else:
                    updated_responses.append(response)
            except (OnboardingQuestion.DoesNotExist, AnswerOption.DoesNotExist):
                continue
        
        return Response({
            'created_count': len(created_responses),
            'updated_count': len(updated_responses),
            'total_processed': len(created_responses) + len(updated_responses)
        })

    @action(detail=False, methods=['get'], url_path='my-responses', permission_classes=[IsAuthenticated])
    def my_responses(self, request):
        """Obtener todas las respuestas del usuario autenticado."""
        user = request.user
        responses = OnboardingResponse.objects.filter(user=user).select_related('question', 'option')
        return Response(OnboardingResponseSerializer(responses, many=True).data)

    @action(detail=False, methods=['get'], url_path='my-status', permission_classes=[IsAuthenticated])
    def my_status(self, request):
        """Estado del onboarding para el usuario autenticado."""
        user = request.user
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        answered_questions = OnboardingResponse.objects.filter(user=user).count()
        
        return Response({
            'user_id': user.user_id,
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'is_complete': answered_questions >= total_questions,
            'progress_percentage': round(
                (answered_questions / total_questions * 100) if total_questions > 0 else 0, 2
            )
        })

    @action(detail=False, methods=['post'], url_path='calculate-my-risk', permission_classes=[IsAuthenticated])
    def calculate_my_risk(self, request):
        """Calcular el nivel de riesgo para el usuario autenticado."""
        user = request.user
        
        responses = OnboardingResponse.objects.filter(
            user=user,
            option__isnull=False
        ).select_related('question', 'option')
        
        if not responses.exists():
            return Response({
                'error': 'No hay respuestas registradas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_risk_score = sum(
            r.option.risk_value * r.question.risk_weight for r in responses
        )
        
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        questions_answered = responses.count()
        
        max_weights = sum(r.question.risk_weight for r in responses)
        max_possible_score = max_weights * 5 if max_weights > 0 else 1
        
        risk_percentage = (total_risk_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        if risk_percentage <= 33:
            risk_level_name = 'Low'
        elif risk_percentage <= 66:
            risk_level_name = 'Medium'
        else:
            risk_level_name = 'High'
        
        risk_level = RiskLevel.objects.filter(name=risk_level_name).first()
        if risk_level:
            user.risk_level = risk_level
            user.save()
        
        UserStatistic.objects.update_or_create(
            user=user,
            metric='onboarding_risk_score',
            defaults={'value': risk_percentage}
        )
        
        return Response({
            'user_id': user.user_id,
            'total_risk_score': total_risk_score,
            'max_possible_score': max_possible_score,
            'risk_percentage': round(risk_percentage, 2),
            'risk_level': risk_level_name,
            'questions_answered': questions_answered,
            'total_questions': total_questions
        })

    @action(detail=False, methods=['get'], url_path='calculate_risk/(?P<user_id>[^/.]+)')
    def calculate_risk(self, request, user_id=None):
        """Calcular nivel de riesgo por user_id (legacy endpoint)."""
        user = get_object_or_404(CyberUser, pk=user_id)
        
        responses = OnboardingResponse.objects.filter(
            user_id=user_id,
            option__isnull=False
        ).select_related('question', 'option')
        
        total_risk_score = sum(
            r.option.risk_value * r.question.risk_weight for r in responses
        )
        
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        questions_answered = responses.count()
        
        max_weights = sum(r.question.risk_weight for r in responses)
        max_possible_score = max_weights * 5 if max_weights > 0 else 1
        
        risk_percentage = (total_risk_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        if risk_percentage <= 33:
            risk_level_name = 'Low'
        elif risk_percentage <= 66:
            risk_level_name = 'Medium'
        else:
            risk_level_name = 'High'
        
        risk_level = RiskLevel.objects.filter(name=risk_level_name).first()
        if risk_level:
            user.risk_level = risk_level
            user.save()
        
        UserStatistic.objects.update_or_create(
            user=user,
            metric='onboarding_risk_score',
            defaults={'value': risk_percentage}
        )
        
        return Response({
            'user_id': user.user_id,
            'total_risk_score': total_risk_score,
            'max_possible_score': max_possible_score,
            'risk_percentage': round(risk_percentage, 2),
            'risk_level': risk_level_name,
            'questions_answered': questions_answered,
            'total_questions': total_questions
        })

    @action(detail=False, methods=['get'], url_path='status/(?P<user_id>[^/.]+)')
    def onboarding_status(self, request, user_id=None):
        """Estado del onboarding por user_id (legacy endpoint)."""
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        answered_questions = OnboardingResponse.objects.filter(user_id=user_id).count()
        
        return Response({
            'user_id': int(user_id),
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'is_complete': answered_questions >= total_questions,
            'progress_percentage': round(
                (answered_questions / total_questions * 100) if total_questions > 0 else 0, 2
            )
        })


class UserStatisticViewSet(viewsets.ModelViewSet):
    queryset = UserStatistic.objects.all()
    serializer_class = UserStatisticSerializer

    def get_queryset(self):
        queryset = UserStatistic.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class GlobalStatisticViewSet(viewsets.ModelViewSet):
    queryset = GlobalStatistic.objects.all()
    serializer_class = GlobalStatisticSerializer

    def get_queryset(self):
        queryset = GlobalStatistic.objects.all()
        country_id = self.request.query_params.get('country_id')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset
