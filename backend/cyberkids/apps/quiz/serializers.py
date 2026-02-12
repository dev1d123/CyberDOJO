from rest_framework import serializers
from .models import (
    Quiz,
    QuizQuestion,
    QuizAlternative,
    QuizHint,
    QuizAnswer,
    QuizSession
)
from .rewards_config import get_coins_reward, get_points_reward, get_expected_questions


class QuizAlternativeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='alternative_id', read_only=True)

    class Meta:
        model = QuizAlternative
        fields = ['id', 'content', 'display_order']


class QuizHintSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='hint_id', read_only=True)

    class Meta:
        model = QuizHint
        fields = ['id', 'content', 'cost_points', 'display_order']


class QuizQuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='question_id', read_only=True)
    alternatives = QuizAlternativeSerializer(many=True, read_only=True)
    hints = QuizHintSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = [
            'id',
            'content',
            'explanation',
            'points',
            'display_order',
            'image_url',
            'alternatives',
            'hints'
        ]


class QuizListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='quiz_id', read_only=True)
    difficulty = serializers.IntegerField(source='difficulty_level', read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    segment = serializers.StringRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'difficulty',
            'base_points',
            'time_limit_seconds',
            'category',
            'segment',
            'image_url',
            'progress',
            'status',
        ]

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    def get_progress(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return None

        session = obj.sessions.filter(
            user=request.user
        ).order_by('-started_at').first()

        total = obj.questions.count()

        if not session:
            return {
                "answered": 0,
                "total": total,
                "correct": 0,
                "percentage": 0
            }

        answered = session.answers.count()
        correct = session.answers.filter(is_correct=True).count()

        percentage = int((answered / total) * 100) if total > 0 else 0
        return {
            "answered": answered,
            "total": total,
            "correct": correct,
            "percentage": percentage
        }

    def get_status(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return "not_started"

        session = obj.sessions.filter(
            user=request.user
        ).order_by('-started_at').first()

        if not session:
            return "not_started"

        return session.status


class QuizDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='quiz_id', read_only=True)
    questions = QuizQuestionSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'difficulty_level',
            'base_points',
            'time_limit_seconds',
            'questions',
            'image_url'
        ]

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class QuizAnswerCreateSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_alternative_id = serializers.IntegerField()
    time_spent_seconds = serializers.IntegerField(required=False)

    def validate(self, attrs):
        request = self.context['request']

        question = QuizQuestion.objects.get(
            question_id=attrs['question_id']
        )

        alternative = QuizAlternative.objects.get(
            alternative_id=attrs['selected_alternative_id'],
            question=question
        )

        session = QuizSession.objects.filter(
            user=request.user,
            quiz=question.quiz,
            status='in_progress'
        ).order_by('-started_at').first()

        if not session:
            raise serializers.ValidationError("No active session found.")

        if session.answers.filter(question=question).exists():
            raise serializers.ValidationError("Question already answered.")

        attrs['question'] = question
        attrs['alternative'] = alternative
        attrs['session'] = session

        return attrs

    def create(self, validated_data):
        session = validated_data['session']
        question = validated_data['question']
        alternative = validated_data['alternative']
        time_spent = validated_data.get('time_spent_seconds')

        is_correct = alternative.is_correct

        answer = QuizAnswer.objects.create(
            session=session,
            question=question,
            selected_alternative=alternative,
            is_correct=is_correct,
            time_spent_seconds=time_spent,
        )

        if is_correct:
            session.total_correct += 1

        session.total_answered += 1
        total = question.quiz.questions.count()

        # Si es la última respuesta, marcar como completado y dar recompensas
        if session.total_answered >= total:
            session.status = 'completed'
            session.ended_at = serializers.Serializer().to_representation(None)  # Usar timezone
            
            # Calcular rewards basado en dificultad
            difficulty = question.quiz.difficulty_level
            session.coins_earned = get_coins_reward(difficulty)
            session.points_earned = get_points_reward(difficulty) * session.total_correct

        session.save()

        return answer


class QuizSessionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='session_id', read_only=True)
    quiz_id = serializers.IntegerField(source='quiz.quiz_id', read_only=True)
    
    class Meta:
        model = QuizSession
        fields = [
            'id',
            'quiz_id',
            'status',
            'attempt_number',
            'total_answered',
            'total_correct',
            'coins_earned',
            'points_earned',
            'started_at',
            'ended_at'
        ]
        read_only_fields = fields
