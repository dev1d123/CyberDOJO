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
        age = user.preferences.age if hasattr(user, 'preferences') and user.preferences else None

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
        """Inicia o crea nueva sesión de quiz para reintento."""
        quiz = self.get_object()
        confirm_retry = bool(request.data.get('confirm_retry'))

        # Buscar la última sesión del usuario para este quiz
        last_session = QuizSession.objects.filter(
            user=request.user,
            quiz=quiz
        ).order_by('-started_at').first()

        # Determinar si es un reintento o si la sesión está "sucia" (tiene respuestas)
        is_retry = last_session and last_session.status == 'completed'
        is_dirty_session = last_session and last_session.status == 'not_started' and last_session.answers.exists()
        needs_confirm = is_retry or is_dirty_session

        if needs_confirm and not confirm_retry:
            return Response({
                "show_warning": True,
                "is_retry": bool(is_retry),
                "is_dirty": bool(is_dirty_session),
                "previous_attempts": last_session.attempt_number if last_session else 0,
                "message": "Confirmar reintento"
            }, status=status.HTTP_200_OK)

        # Si es un reintento O la sesión tiene respuestas, CREAR una nueva sesión
        if is_retry or is_dirty_session:
            session = QuizSession.objects.create(
                user=request.user,
                quiz=quiz,
                status='not_started',
                attempt_number=last_session.attempt_number + 1 if last_session else 1
            )
            if is_retry:
                print(f"🔄 Reintento - Nueva sesión creada: {session.session_id}, Intento #{session.attempt_number}")
            else:
                print(f"🧹 Sesión sucia detectada - Nueva sesión creada: {session.session_id}, Intento #{session.attempt_number}")
        elif not last_session:
            # Primera vez - crear sesión inicial
            session = QuizSession.objects.create(
                user=request.user,
                quiz=quiz,
                status='not_started',
                attempt_number=1
            )
            print(f"🆕 Primera vez - Sesión creada: {session.session_id}")
        else:
            # Sesión existente limpia (sin respuestas) - reutilizar
            session = last_session
            print(f"♻️ Reutilizando sesión limpia: {session.session_id}")

        # Serializar el quiz completo con todas las preguntas
        quiz_serializer = QuizDetailSerializer(quiz)
        session_serializer = QuizSessionSerializer(session)

        return Response({
            "session": session_serializer.data,
            "quiz": quiz_serializer.data,
            "show_warning": False,
            "is_retry": bool(is_retry),
            "previous_attempts": last_session.attempt_number if last_session else 0,
            "message": "Sesión iniciada"
        }, status=status.HTTP_200_OK)

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

        # Si es la última respuesta, incluir datos de finalización
        session = answer.session
        if session.status == 'completed':
            response_data.update({
                "quiz_completed": True,
                "total_correct": session.total_correct,
                "total_answered": session.total_answered,
                "coins_earned": session.coins_earned,  # Mantendrá 0 en reintentos
                "points_earned": session.points_earned,
                "percentage": int((session.total_correct / session.total_answered) * 100) if session.total_answered > 0 else 0,
                "cybercreds_balance": session.user.cybercreds
            })

            # Incluir logros desbloqueados (si los hay)
            unlocked = getattr(answer, '_unlocked_achievements', [])
            if unlocked:
                response_data["achievements_unlocked"] = unlocked

        return Response(response_data, status=status.HTTP_201_CREATED)
