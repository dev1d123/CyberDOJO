from rest_framework import serializers
from django.utils import timezone
from .models import (
    Quiz,
    QuizQuestion,
    QuizAlternative,
    QuizHint,
    QuizAnswer,
    QuizSession
)
from .rewards_config import get_coins_reward, get_points_reward, get_expected_questions
from apps.progression.services import AchievementService


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

        answered = session.total_answered or session.answers.count()
        correct = session.total_correct or session.answers.filter(is_correct=True).count()

        # Ensure answered doesn't exceed total (in case of manual data entry)
        answered = min(answered, total)
        correct = min(correct, total)

        # Percentage represents accuracy (correct / total)
        percentage = int((correct / total) * 100) if total > 0 else 0
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

        # Usar el session_id específico enviado por el frontend
        session_id = self.initial_data.get('session_id')
        print(f"🔍 DEBUG - session_id recibido: {session_id}")
        if not session_id:
            raise serializers.ValidationError("session_id is required.")
        
        session = QuizSession.objects.filter(
            session_id=session_id,
            user=request.user
        ).first()

        if not session:
            print(f"❌ DEBUG - Sesión no encontrada con session_id={session_id} para user={request.user.username}")
            raise serializers.ValidationError("Session not found or does not belong to this user.")
        
        print(f"✅ DEBUG - Sesión encontrada: {session.session_id}, status={session.status}, attempt={session.attempt_number}")
        
        # Verificar si la pregunta ya fue respondida en ESTA sesión
        existing_answer = session.answers.filter(question=question).first()
        if existing_answer:
            print(f"⚠️ DEBUG - Pregunta {question.question_id} YA respondida en sesión {session.session_id}")
            print(f"📊 DEBUG - Total respuestas en sesión: {session.answers.count()}")
            raise serializers.ValidationError("Question already answered.")
        
        print(f"✅ DEBUG - Pregunta {question.question_id} NO respondida aún en sesión {session.session_id}")

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

        # Si es la última respuesta, marcar como completado y calcular recompensas
        if session.total_answered >= total:
            session.status = 'completed'
            session.ended_at = timezone.now()
            
            # Solo dar recompensas en el primer intento
            if session.attempt_number == 1:
                difficulty = question.quiz.difficulty_level
                session.coins_earned = get_coins_reward(difficulty)
                session.points_earned = get_points_reward(difficulty) * session.total_correct

                # Sumar coins a los cybercreds del usuario
                user = session.user
                user.cybercreds = (user.cybercreds or 0) + session.coins_earned
                user.save(update_fields=['cybercreds'])

                print(f"💰 Primer intento - Recompensas: {session.coins_earned} monedas, {session.points_earned} puntos")
            else:
                # Reintentos: sin recompensas
                session.coins_earned = 0
                session.points_earned = 0
                print(f"🔄 Reintento #{session.attempt_number} - Sin recompensas")

            # Verificar y desbloquear logros
            unlocked_achievements = []
            try:
                unlocked = AchievementService.on_quiz_completed(session.user, session)
                if unlocked:
                    unlocked_achievements = [{
                        'achievement_id': a['achievement'].achievement_id,
                        'name': a['achievement'].name,
                        'description': a['achievement'].description,
                        'category': a['achievement'].category,
                        'icon': a['achievement'].icon.url if a['achievement'].icon else None,
                        'cybercreds_reward': a['achievement'].cybercreds_reward,
                        'xp_reward': a['achievement'].xp_reward,
                    } for a in unlocked]
                    print(f"🏆 Logros desbloqueados: {[a['name'] for a in unlocked_achievements]}")
            except Exception as e:
                print(f"⚠️ Error verificando logros: {e}")

            # Adjuntar al answer para que la vista pueda leerlos
            answer._unlocked_achievements = unlocked_achievements

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
