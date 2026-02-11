from rest_framework import serializers
from .models import Quiz, QuizQuestion, QuizAlternative, QuizHint, QuizAnswer, QuizSession


class QuizAlternativeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='alternative_id', read_only=True)

    class Meta:
        model = QuizAlternative
        fields = ['id', 'content', 'is_correct', 'feedback', 'display_order']


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
        fields = ['id', 'content', 'explanation', 'points', 'display_order', 'image_url', 'alternatives', 'hints']


class QuizListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='quiz_id', read_only=True)
    difficulty = serializers.IntegerField(source='difficulty_level', read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    segment = serializers.StringRelatedField(read_only=True)

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
            'segment'
        ]


class QuizDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='quiz_id', read_only=True)
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'difficulty_level', 'base_points', 'time_limit_seconds', 'questions']


class QuizAnswerCreateSerializer(serializers.Serializer):
    # Accept either session_id (existing) or will create a session for authenticated user
    session_id = serializers.IntegerField(required=False)
    question_id = serializers.IntegerField()
    selected_alternative_id = serializers.IntegerField()
    time_spent_seconds = serializers.IntegerField(required=False)

    def validate(self, attrs):
        # Validate question and alternative existence
        qid = attrs.get('question_id')
        aid = attrs.get('selected_alternative_id')
        try:
            question = QuizQuestion.objects.get(question_id=qid)
        except QuizQuestion.DoesNotExist:
            raise serializers.ValidationError({'question_id': 'Invalid question_id'})

        try:
            alt = QuizAlternative.objects.get(alternative_id=aid, question=question)
        except QuizAlternative.DoesNotExist:
            raise serializers.ValidationError({'selected_alternative_id': 'Invalid alternative for the question'})

        attrs['_question_obj'] = question
        attrs['_alternative_obj'] = alt
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        session_id = validated_data.get('session_id')
        question = validated_data['_question_obj']
        alternative = validated_data['_alternative_obj']
        time_spent = validated_data.get('time_spent_seconds')

        session = None
        if session_id:
            try:
                session = QuizSession.objects.get(session_id=session_id)
            except QuizSession.DoesNotExist:
                session = None

        if not session and request and request.user and request.user.is_authenticated:
            # create a new session for the user and question.quiz
            session = QuizSession.objects.create(user=request.user, quiz=question.quiz)

        if not session:
            raise serializers.ValidationError({'session': 'Session not provided and user anonymous'})

        is_correct = alternative.is_correct
        answer = QuizAnswer.objects.create(
            session=session,
            question=question,
            selected_alternative=alternative,
            is_correct=is_correct,
            time_spent_seconds=time_spent,
        )

        return answer
