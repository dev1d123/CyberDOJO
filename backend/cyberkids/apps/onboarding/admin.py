from django.contrib import admin
from .models import (
    OnboardingQuestion,
    AnswerOption,
    OnboardingResponse,
    UserStatistic,
    GlobalStatistic
)


@admin.register(OnboardingQuestion)
class OnboardingQuestionAdmin(admin.ModelAdmin):
    """
    Administración de las preguntas del cuestionario de onboarding.
    Permite gestionar las preguntas, su categoría y orden de presentación.
    """
    list_display = ['question_id', 'category', 'question_text_preview', 'order_index', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question_text', 'category']
    ordering = ['order_index', 'question_id']
    list_editable = ['order_index', 'is_active']
    
    def question_text_preview(self, obj):
        """Muestra una vista previa del texto de la pregunta"""
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'Texto de la Pregunta'


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    """
    Administración de las opciones de respuesta.
    Permite configurar las respuestas disponibles y su valor de riesgo asociado.
    """
    list_display = ['option_id', 'question', 'option_text_preview', 'risk_value', 'order_index']
    list_filter = ['question__category', 'risk_value']
    search_fields = ['option_text', 'question__question_text']
    ordering = ['question', 'order_index']
    list_editable = ['risk_value', 'order_index']
    
    def option_text_preview(self, obj):
        """Muestra una vista previa del texto de la opción"""
        return obj.option_text[:40] + '...' if len(obj.option_text) > 40 else obj.option_text
    option_text_preview.short_description = 'Texto de la Opción'


@admin.register(OnboardingResponse)
class OnboardingResponseAdmin(admin.ModelAdmin):
    """
    Administración de las respuestas de onboarding.
    Permite visualizar las respuestas que los usuarios dieron durante el onboarding.
    """
    list_display = ['response_id', 'user', 'question', 'selected_option', 'response_timestamp']
    list_filter = ['response_timestamp', 'question__category']
    search_fields = ['user__username', 'user__email', 'question__question_text']
    ordering = ['-response_timestamp']
    readonly_fields = ['response_timestamp']
    
    # No permitir modificaciones masivas para mantener la integridad
    def has_add_permission(self, request):
        return False


@admin.register(UserStatistic)
class UserStatisticAdmin(admin.ModelAdmin):
    """
    Administración de estadísticas individuales de usuario.
    Permite monitorear el progreso y actividad de cada usuario en la plataforma.
    """
    list_display = [
        'user',
        'onboarding_completed',
        'total_playtime_minutes',
        'minigames_completed',
        'simulations_completed',
        'success_rate',
        'current_streak',
        'last_active_date'
    ]
    list_filter = [
        'onboarding_completed',
        'last_active_date',
        'onboarding_completion_date'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'success_rate']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'onboarding_completed', 'onboarding_completion_date')
        }),
        ('Estadísticas de Actividad', {
            'fields': (
                'total_playtime_minutes',
                'minigames_completed',
                'simulations_completed',
                'achievements_unlocked',
                'pet_interactions'
            )
        }),
        ('Rendimiento', {
            'fields': (
                'correct_answers',
                'incorrect_answers',
                'success_rate'
            )
        }),
        ('Rachas y Actividad', {
            'fields': (
                'current_streak',
                'longest_streak',
                'last_active_date'
            )
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GlobalStatistic)
class GlobalStatisticAdmin(admin.ModelAdmin):
    """
    Administración de estadísticas globales por país.
    Permite visualizar y comparar métricas agregadas entre diferentes regiones.
    """
    list_display = [
        'country_name',
        'total_users',
        'average_risk_level',
        'average_success_rate',
        'total_simulations_completed',
        'total_minigames_completed',
        'last_updated'
    ]
    list_filter = ['last_updated', 'country_name']
    search_fields = ['country_name']
    readonly_fields = ['last_updated', 'created_at']
    ordering = ['-total_users']
    
    fieldsets = (
        ('Información del País', {
            'fields': ('country_id', 'country_name')
        }),
        ('Métricas de Usuarios', {
            'fields': (
                'total_users',
                'average_risk_level',
                'most_common_risk_category'
            )
        }),
        ('Actividad y Rendimiento', {
            'fields': (
                'total_simulations_completed',
                'total_minigames_completed',
                'average_success_rate',
                'total_playtime_hours'
            )
        }),
        ('Fechas', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )
