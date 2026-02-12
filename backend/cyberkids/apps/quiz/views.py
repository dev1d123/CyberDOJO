from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Quiz, QuizSession, AudienceSegment
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuizAnswerCreateSerializer,
    QuizSessionSerializer
)
from .rewards_config import get_segment_for_age, get_expected_questions, get_coins_reward


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.filter(is_active=True).order_by('display_order')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        elif self.action == 'start':
            return QuizSessionSerializer
        elif self.action == 'submit':
            return QuizAnswerCreateSerializer
        return QuizDetailSerializer

    def get_queryset(self):
        """Filtrar quizzes por edad del usuario."""
        user = self.request.user
        queryset = super().get_queryset()

        # Obtener edad del usuario desde preferences
        try:
            age = user.preferences.get('age') if hasattr(user, 'preferences') else None
        except:
            age = None

        # Si no hay edad, mostrar quizzes de nivel medio (defecto)
        if not age:
            segment_name = "Niños 11-14"  # Defecto
        else:
            segment_code = get_segment_for_age(age)
            # Mapear código a nombre en BD
            segment_map = {
                'junior': "Niños 7-10",
                'middle': "Niños 11-14",
                'senior': "Adolescentes 15+"
            }
            segment_name = segment_map.get(segment_code, "Niños 11-14")

        # Filtrar por segmento
        try:
            segment = AudienceSegment.objects.get(name=segment_name)
            queryset = queryset.filter(segment=segment)
        except AudienceSegment.DoesNotExist:
            # Si no existe el segmento, no filtrar
            pass

        return queryset

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Inicia una nueva sesión de quiz."""
        quiz = self.get_object()

        # Buscar sesión activa
        existing_session = QuizSession.objects.filter(
            user=request.user,
            quiz=quiz,
            status='in_progress'
        ).first()

        if existing_session:
            return Response({
                "session_id": existing_session.session_id,
                "status": "already_started",
                "message": "Ya hay una sesión en progreso"
            }, status=status.HTTP_200_OK)

        # Verificar si hay intentos previos completados
        previous_sessions = QuizSession.objects.filter(
            user=request.user,
            quiz=quiz,
            status='completed'
        ).count()

        # Crear nueva sesión
        session = QuizSession.objects.create(
            user=request.user,
            quiz=quiz,
            status='in_progress',
            attempt_number=previous_sessions + 1
        )

        serializer = QuizSessionSerializer(session)

        return Response({
            **serializer.data,
            "status": "started",
            "previous_attempts": previous_sessions,
            "show_warning": previous_sessions > 0,  # Mostrar modal si hay intentos previos
            "message": "Sesión iniciada" if previous_sessions == 0 else "Sesión reiniciada"
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Envía respuesta a pregunta."""
        serializer = QuizAnswerCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        # Obtener la alternativa para el feedback
        alternative = answer.selected_alternative
        question = answer.question

        response_data = {
            "is_correct": answer.is_correct,
            "feedback": alternative.feedback,
            "explanation": question.explanation,
            "correct_alternative": next(
                (alt.content for alt in question.alternatives.all() if alt.is_correct),
                None
            )
        }

        # Si es la última respuesta, incluir datos de finalización e información de rewards
        session = answer.session
        if session.status == 'completed':
            difficulty = question.quiz.difficulty_level
            coins_reward = get_coins_reward(difficulty)
            
            response_data.update({
                "quiz_completed": True,
                "total_correct": session.total_correct,
                "total_answered": session.total_answered,
                "coins_earned": session.coins_earned,
                "points_earned": session.points_earned,
                "percentage": int((session.total_correct / session.total_answered) * 100) if session.total_answered > 0 else 0
            })

        return Response(response_data, status=status.HTTP_201_CREATED)
