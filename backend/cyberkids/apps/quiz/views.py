from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .models import Quiz, QuizQuestion, QuizAlternative, QuizAnswer
from .serializers import (
	QuizListSerializer, QuizDetailSerializer, QuizAnswerCreateSerializer,
)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
	"""Provides `list` and `retrieve` for quizzes."""
	queryset = Quiz.objects.filter(is_active=True).order_by('display_order')
	permission_classes = [AllowAny]

	def get_serializer_class(self):
		if self.action == 'list':
			return QuizListSerializer
		return QuizDetailSerializer

	@action(detail=True, methods=['post'], url_path='answers', permission_classes=[AllowAny])
	def submit_answer(self, request, pk=None):
		"""Endpoint: POST /api/quiz/quizzes/{pk}/answers/ to submit an answer."""
		serializer = QuizAnswerCreateSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		answer = serializer.save()
		return Response({'status': 'created', 'answer_id': answer.answer_id}, status=status.HTTP_201_CREATED)
