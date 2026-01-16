from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Minigame, SwipeQuestion, MinigameSession, SwipeResponse
from .serializers import MinigameSerializer, SwipeQuestionSerializer, MinigameSessionSerializer, SwipeResponseSerializer
from apps.cyberUser.models import CyberUser
from apps.progression.models import CreditTransaction


class MinigameViewSet(viewsets.ModelViewSet):
    queryset = Minigame.objects.all()
    serializer_class = MinigameSerializer
    permission_classes = [AllowAny]

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

    @action(detail=True, methods=['get'], url_path='questions/random')
    def random_questions(self, request, pk=None):
        """Obtiene preguntas aleatorias de un minijuego."""
        minigame = self.get_object()
        count = int(request.query_params.get('count', 10))
        questions = minigame.questions.order_by('?')[:count]
        return Response(SwipeQuestionSerializer(questions, many=True).data)


class SwipeQuestionViewSet(viewsets.ModelViewSet):
    queryset = SwipeQuestion.objects.all()
    serializer_class = SwipeQuestionSerializer
    permission_classes = [AllowAny]

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
        queryset = MinigameSession.objects.all().order_by('-started_at')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request):
        """Inicia una nueva sesión de minijuego para el usuario autenticado."""
        user = request.user
        minigame_id = request.data.get('minigame_id')

        if not minigame_id:
            return Response({'error': 'minigame_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        minigame = get_object_or_404(Minigame, pk=minigame_id)

        session = MinigameSession.objects.create(user=user, minigame=minigame)
        return Response(MinigameSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def finish(self, request, pk=None):
        """Finaliza una sesión y calcula puntos."""
        session = self.get_object()
        
        # Verificar que la sesión pertenece al usuario
        if session.user.user_id != request.user.user_id:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
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

        # Registrar transacción
        CreditTransaction.objects.create(
            user=user,
            amount=session.points_earned,
            transaction_type='minigame',
            description=f'Minijuego: {session.minigame.name}',
            reference_id=session.session_id,
            reference_type='minigame_session'
        )

        return Response({
            'session': MinigameSessionSerializer(session).data,
            'points_earned': session.points_earned,
            'new_cybercreds_balance': user.cybercreds
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_sessions(self, request):
        """Lista las sesiones del usuario autenticado."""
        sessions = MinigameSession.objects.filter(user=request.user).order_by('-started_at')
        return Response(MinigameSessionSerializer(sessions, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_stats(self, request):
        """Estadísticas de minijuegos del usuario autenticado."""
        user = request.user
        sessions = MinigameSession.objects.filter(user=user)
        
        total_sessions = sessions.count()
        total_points = sum(s.points_earned or 0 for s in sessions)
        total_correct = sum(s.correct_answers or 0 for s in sessions)
        total_incorrect = sum(s.incorrect_answers or 0 for s in sessions)
        total_time = sum(s.time_spent_sec or 0 for s in sessions)
        
        return Response({
            'total_sessions': total_sessions,
            'total_points': total_points,
            'total_correct': total_correct,
            'total_incorrect': total_incorrect,
            'accuracy': round((total_correct / (total_correct + total_incorrect) * 100) if (total_correct + total_incorrect) > 0 else 0, 1),
            'total_time_seconds': total_time,
        })


class SwipeResponseViewSet(viewsets.ModelViewSet):
    queryset = SwipeResponse.objects.all()
    serializer_class = SwipeResponseSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request):
        """Envía una respuesta y verifica si es correcta."""
        session_id = request.data.get('minigame_session_id')
        question_id = request.data.get('question_id')
        user_answer = request.data.get('user_answer')
        response_time_ms = request.data.get('response_time_ms')

        if not all([session_id, question_id, user_answer is not None]):
            return Response({
                'error': 'Se requieren minigame_session_id, question_id y user_answer'
            }, status=status.HTTP_400_BAD_REQUEST)

        session = get_object_or_404(MinigameSession, pk=session_id)
        
        # Verificar que la sesión pertenece al usuario
        if session.user.user_id != request.user.user_id:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
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

    @action(detail=False, methods=['post'], url_path='submit-batch', permission_classes=[IsAuthenticated])
    def submit_batch(self, request):
        """Envía múltiples respuestas en lote."""
        session_id = request.data.get('minigame_session_id')
        answers = request.data.get('answers', [])

        if not session_id or not answers:
            return Response({
                'error': 'Se requieren minigame_session_id y answers'
            }, status=status.HTTP_400_BAD_REQUEST)

        session = get_object_or_404(MinigameSession, pk=session_id)
        
        # Verificar que la sesión pertenece al usuario
        if session.user.user_id != request.user.user_id:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        results = []
        correct_count = 0
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            user_answer = answer_data.get('user_answer')
            response_time_ms = answer_data.get('response_time_ms')
            
            if not question_id or user_answer is None:
                continue
                
            try:
                question = SwipeQuestion.objects.get(pk=question_id)
                is_correct = user_answer == question.correct_answer
                
                if is_correct:
                    correct_count += 1
                
                response = SwipeResponse.objects.create(
                    minigame_session=session,
                    question=question,
                    user_answer=user_answer,
                    is_correct=is_correct,
                    response_time_ms=response_time_ms
                )
                
                results.append({
                    'question_id': question_id,
                    'is_correct': is_correct,
                    'correct_answer': question.correct_answer
                })
            except SwipeQuestion.DoesNotExist:
                continue

        return Response({
            'processed': len(results),
            'correct': correct_count,
            'incorrect': len(results) - correct_count,
            'results': results
        }, status=status.HTTP_201_CREATED)
