from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Minigame, SwipeQuestion, MinigameSession, SwipeResponse
from .serializers import MinigameSerializer, SwipeQuestionSerializer, MinigameSessionSerializer, SwipeResponseSerializer
from apps.cyberUser.models import CyberUser


class MinigameViewSet(viewsets.ModelViewSet):
    queryset = Minigame.objects.all()
    serializer_class = MinigameSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lista minijuegos activos."""
        minigames = Minigame.objects.filter(is_active=True)
        return Response(MinigameSerializer(minigames, many=True).data)

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Obtiene preguntas de un minijuego."""
        minigame = self.get_object()
        questions = minigame.questions.all()
        return Response(SwipeQuestionSerializer(questions, many=True).data)


class SwipeQuestionViewSet(viewsets.ModelViewSet):
    queryset = SwipeQuestion.objects.all()
    serializer_class = SwipeQuestionSerializer

    def get_queryset(self):
        queryset = SwipeQuestion.objects.all()
        minigame_id = self.request.query_params.get('minigame_id')
        country_id = self.request.query_params.get('country_id')
        if minigame_id:
            queryset = queryset.filter(minigame_id=minigame_id)
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset


class MinigameSessionViewSet(viewsets.ModelViewSet):
    queryset = MinigameSession.objects.all()
    serializer_class = MinigameSessionSerializer

    def get_queryset(self):
        queryset = MinigameSession.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Inicia una nueva sesión de minijuego."""
        user_id = request.data.get('user_id')
        minigame_id = request.data.get('minigame_id')

        user = get_object_or_404(CyberUser, pk=user_id)
        minigame = get_object_or_404(Minigame, pk=minigame_id)

        session = MinigameSession.objects.create(user=user, minigame=minigame)
        return Response(MinigameSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """Finaliza una sesión y calcula puntos."""
        session = self.get_object()
        time_spent_sec = request.data.get('time_spent_sec')

        if time_spent_sec:
            session.time_spent_sec = time_spent_sec

        # Calcular respuestas correctas e incorrectas
        responses = session.responses.all()
        correct = responses.filter(is_correct=True).count()
        incorrect = responses.filter(is_correct=False).count()

        session.correct_answers = correct
        session.incorrect_answers = incorrect
        session.points_earned = correct * session.minigame.base_points
        session.save()

        # Añadir cybercreds al usuario
        user = session.user
        user.cybercreds += session.points_earned
        user.save(update_fields=['cybercreds'])

        return Response(MinigameSessionSerializer(session).data)


class SwipeResponseViewSet(viewsets.ModelViewSet):
    queryset = SwipeResponse.objects.all()
    serializer_class = SwipeResponseSerializer

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Envía una respuesta y verifica si es correcta."""
        session_id = request.data.get('minigame_session_id')
        question_id = request.data.get('question_id')
        user_answer = request.data.get('user_answer')
        response_time_ms = request.data.get('response_time_ms')

        session = get_object_or_404(MinigameSession, pk=session_id)
        question = get_object_or_404(SwipeQuestion, pk=question_id)

        is_correct = user_answer == question.correct_answer

        response = SwipeResponse.objects.create(
            minigame_session=session,
            question=question,
            user_answer=user_answer,
            is_correct=is_correct,
            response_time_ms=response_time_ms
        )

        return Response({
            'response': SwipeResponseSerializer(response).data,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation
        }, status=status.HTTP_201_CREATED)
