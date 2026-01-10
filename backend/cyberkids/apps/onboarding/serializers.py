from rest_framework import serializers
from .models import (
    OnboardingQuestion,
    AnswerOption,
    OnboardingResponse,
    UserStatistic,
    GlobalStatistic
)


class AnswerOptionSerializer(serializers.ModelSerializer):
    """
    Serializador para las opciones de respuesta.
    Incluye toda la información necesaria para mostrar las opciones al usuario,
    pero excluye el risk_value para evitar que los usuarios vean los valores de riesgo.
    """
    class Meta:
        model = AnswerOption
        fields = ['option_id', 'option_text', 'order_index']
        read_only_fields = ['option_id']


class AnswerOptionDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detallado para opciones de respuesta (uso administrativo).
    Incluye el risk_value para análisis y configuración.
    """
    class Meta:
        model = AnswerOption
        fields = ['option_id', 'question', 'option_text', 'risk_value', 'order_index', 'created_at', 'updated_at']
        read_only_fields = ['option_id', 'created_at', 'updated_at']


class OnboardingQuestionSerializer(serializers.ModelSerializer):
    """
    Serializador para las preguntas de onboarding.
    Incluye las opciones de respuesta anidadas para facilitar la presentación
    del cuestionario completo al usuario.
    """
    options = AnswerOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = OnboardingQuestion
        fields = [
            'question_id',
            'question_text',
            'category',
            'order_index',
            'options'
        ]
        read_only_fields = ['question_id']


class OnboardingQuestionDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detallado para preguntas (uso administrativo).
    Incluye información completa incluyendo metadatos de gestión.
    """
    options = AnswerOptionDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = OnboardingQuestion
        fields = [
            'question_id',
            'question_text',
            'category',
            'order_index',
            'is_active',
            'created_at',
            'updated_at',
            'options'
        ]
        read_only_fields = ['question_id', 'created_at', 'updated_at']


class OnboardingResponseSerializer(serializers.ModelSerializer):
    """
    Serializador para las respuestas del usuario al cuestionario.
    Permite registrar y consultar las respuestas del onboarding.
    """
    user_id = serializers.IntegerField(source='user.user_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    selected_option_text = serializers.CharField(source='selected_option.option_text', read_only=True)
    risk_value = serializers.IntegerField(source='selected_option.risk_value', read_only=True)
    
    class Meta:
        model = OnboardingResponse
        fields = [
            'response_id',
            'user_id',
            'username',
            'question',
            'question_text',
            'selected_option',
            'selected_option_text',
            'risk_value',
            'response_timestamp'
        ]
        read_only_fields = ['response_id', 'response_timestamp']


class OnboardingResponseCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear respuestas de onboarding.
    Simplificado para el proceso de registro, solo requiere los IDs necesarios.
    """
    class Meta:
        model = OnboardingResponse
        fields = ['user', 'question', 'selected_option']
    
    def validate(self, data):
        """
        Valida que la opción seleccionada pertenezca a la pregunta indicada.
        """
        if data['selected_option'].question != data['question']:
            raise serializers.ValidationError(
                "La opción seleccionada no pertenece a la pregunta indicada."
            )
        return data


class UserStatisticSerializer(serializers.ModelSerializer):
    """
    Serializador para las estadísticas individuales del usuario.
    Incluye todas las métricas de progreso y rendimiento.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = UserStatistic
        fields = [
            'stat_id',
            'user',
            'username',
            'total_playtime_minutes',
            'minigames_completed',
            'simulations_completed',
            'correct_answers',
            'incorrect_answers',
            'success_rate',
            'current_streak',
            'longest_streak',
            'last_active_date',
            'achievements_unlocked',
            'pet_interactions',
            'onboarding_completed',
            'onboarding_completion_date',
            'updated_at'
        ]
        read_only_fields = ['stat_id', 'updated_at', 'success_rate']


class UserStatisticSummarySerializer(serializers.ModelSerializer):
    """
    Serializador resumido de estadísticas del usuario.
    Para mostrar información básica en el perfil o dashboard.
    """
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = UserStatistic
        fields = [
            'total_playtime_minutes',
            'minigames_completed',
            'simulations_completed',
            'success_rate',
            'current_streak',
            'achievements_unlocked',
            'onboarding_completed'
        ]
        read_only_fields = fields


class GlobalStatisticSerializer(serializers.ModelSerializer):
    """
    Serializador para estadísticas globales por país.
    Proporciona métricas agregadas para análisis comparativo entre regiones.
    """
    class Meta:
        model = GlobalStatistic
        fields = [
            'global_stat_id',
            'country_id',
            'country_name',
            'total_users',
            'average_risk_level',
            'total_simulations_completed',
            'total_minigames_completed',
            'average_success_rate',
            'total_playtime_hours',
            'most_common_risk_category',
            'last_updated'
        ]
        read_only_fields = ['global_stat_id', 'last_updated']


class GlobalStatisticSummarySerializer(serializers.ModelSerializer):
    """
    Serializador resumido de estadísticas globales.
    Para mostrar comparativas rápidas entre países.
    """
    class Meta:
        model = GlobalStatistic
        fields = [
            'country_name',
            'total_users',
            'average_risk_level',
            'average_success_rate'
        ]
        read_only_fields = fields


class OnboardingProgressSerializer(serializers.Serializer):
    """
    Serializador para el progreso general del onboarding.
    Combina información del cuestionario y las respuestas del usuario.
    """
    total_questions = serializers.IntegerField()
    answered_questions = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    is_completed = serializers.BooleanField()
    average_risk_value = serializers.FloatField()
    
    class Meta:
        fields = [
            'total_questions',
            'answered_questions',
            'progress_percentage',
            'is_completed',
            'average_risk_value'
        ]
