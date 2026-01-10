"""
Models for RF-06: Initial Risk Identification (Onboarding).

Tables:
- onboarding_question: Onboarding questionnaire questions
- answer_option: Multiple choice options with risk values
- onboarding_response: User's responses to onboarding questions
- user_statistic: Individual user statistics
- global_statistic: Platform-wide statistics by country
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User


class OnboardingQuestion(models.Model):
    """
    Modelo para almacenar las preguntas del cuestionario de onboarding.
    Cada pregunta se utiliza para evaluar el nivel de riesgo inicial del usuario
    en temas de ciberseguridad.
    """
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField(
        help_text="Texto de la pregunta del cuestionario de onboarding"
    )
    category = models.CharField(
        max_length=100,
        help_text="Categoría de la pregunta (ej: privacidad, contraseñas, redes sociales)"
    )
    order_index = models.IntegerField(
        default=0,
        help_text="Orden en el que se presenta la pregunta en el cuestionario"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la pregunta está activa y debe mostrarse"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'onboarding_question'
        ordering = ['order_index', 'question_id']
        verbose_name = 'Pregunta de Onboarding'
        verbose_name_plural = 'Preguntas de Onboarding'

    def __str__(self):
        return f"Q{self.question_id}: {self.question_text[:50]}..."


class AnswerOption(models.Model):
    """
    Modelo para almacenar las opciones de respuesta de cada pregunta.
    Cada opción tiene un valor de riesgo asociado que se utiliza para
    calcular el nivel de riesgo del usuario.
    """
    option_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        OnboardingQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        help_text="Pregunta a la que pertenece esta opción"
    )
    option_text = models.TextField(
        help_text="Texto de la opción de respuesta"
    )
    risk_value = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Valor de riesgo asociado (0=sin riesgo, 10=alto riesgo)"
    )
    order_index = models.IntegerField(
        default=0,
        help_text="Orden en el que se presenta la opción"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'answer_option'
        ordering = ['question', 'order_index']
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'

    def __str__(self):
        return f"Opción {self.option_id}: {self.option_text[:30]}... (Riesgo: {self.risk_value})"


class OnboardingResponse(models.Model):
    """
    Modelo para almacenar las respuestas del usuario al cuestionario de onboarding.
    Registra qué opción seleccionó el usuario para cada pregunta durante el proceso
    de registro inicial.
    """
    response_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='onboarding_responses',
        help_text="Usuario que realizó el onboarding"
    )
    question = models.ForeignKey(
        OnboardingQuestion,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Pregunta respondida"
    )
    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
        related_name='user_responses',
        help_text="Opción seleccionada por el usuario"
    )
    response_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se registró la respuesta"
    )

    class Meta:
        db_table = 'onboarding_response'
        ordering = ['-response_timestamp']
        verbose_name = 'Respuesta de Onboarding'
        verbose_name_plural = 'Respuestas de Onboarding'
        # Un usuario solo puede responder una vez cada pregunta
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username} - Q{self.question.question_id}"


class UserStatistic(models.Model):
    """
    Modelo para almacenar estadísticas individuales de cada usuario.
    Estas métricas se utilizan para trackear el progreso y comportamiento
    del usuario dentro de la plataforma.
    """
    stat_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='statistics',
        help_text="Usuario al que pertenecen estas estadísticas"
    )
    total_playtime_minutes = models.IntegerField(
        default=0,
        help_text="Tiempo total de juego en minutos"
    )
    minigames_completed = models.IntegerField(
        default=0,
        help_text="Número total de minijuegos completados"
    )
    simulations_completed = models.IntegerField(
        default=0,
        help_text="Número de simulaciones de ingeniería social completadas"
    )
    correct_answers = models.IntegerField(
        default=0,
        help_text="Número de respuestas correctas en simulaciones"
    )
    incorrect_answers = models.IntegerField(
        default=0,
        help_text="Número de respuestas incorrectas"
    )
    current_streak = models.IntegerField(
        default=0,
        help_text="Racha actual de días consecutivos jugando"
    )
    longest_streak = models.IntegerField(
        default=0,
        help_text="Racha más larga de días consecutivos"
    )
    last_active_date = models.DateField(
        null=True,
        blank=True,
        help_text="Última fecha en que el usuario estuvo activo"
    )
    achievements_unlocked = models.IntegerField(
        default=0,
        help_text="Número de logros desbloqueados"
    )
    pet_interactions = models.IntegerField(
        default=0,
        help_text="Número de interacciones con la mascota virtual"
    )
    onboarding_completed = models.BooleanField(
        default=False,
        help_text="Indica si el usuario completó el proceso de onboarding"
    )
    onboarding_completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se completó el onboarding"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_statistic'
        verbose_name = 'Estadística de Usuario'
        verbose_name_plural = 'Estadísticas de Usuario'

    def __str__(self):
        return f"Estadísticas de {self.user.username}"

    @property
    def success_rate(self):
        """
        Calcula el porcentaje de respuestas correctas del usuario.
        """
        total_answers = self.correct_answers + self.incorrect_answers
        if total_answers == 0:
            return 0
        return round((self.correct_answers / total_answers) * 100, 2)


class GlobalStatistic(models.Model):
    """
    Modelo para almacenar estadísticas globales agregadas por país.
    Permite comparar el rendimiento entre diferentes regiones y generar
    insights sobre patrones de riesgo por ubicación geográfica.
    """
    global_stat_id = models.AutoField(primary_key=True)
    country_id = models.IntegerField(
        help_text="ID del país (referencia a la tabla country en users)"
    )
    country_name = models.CharField(
        max_length=100,
        help_text="Nombre del país para fácil referencia"
    )
    total_users = models.IntegerField(
        default=0,
        help_text="Número total de usuarios de este país"
    )
    average_risk_level = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text="Nivel de riesgo promedio de usuarios en este país"
    )
    total_simulations_completed = models.IntegerField(
        default=0,
        help_text="Total de simulaciones completadas por usuarios del país"
    )
    total_minigames_completed = models.IntegerField(
        default=0,
        help_text="Total de minijuegos completados por usuarios del país"
    )
    average_success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tasa de éxito promedio en respuestas (porcentaje)"
    )
    total_playtime_hours = models.IntegerField(
        default=0,
        help_text="Tiempo total de juego en horas de todos los usuarios"
    )
    most_common_risk_category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Categoría de riesgo más común entre los usuarios"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización de estas estadísticas"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'global_statistic'
        ordering = ['-total_users']
        verbose_name = 'Estadística Global'
        verbose_name_plural = 'Estadísticas Globales'
        # Solo puede haber un registro de estadísticas por país
        unique_together = ['country_id']

    def __str__(self):
        return f"Estadísticas Globales - {self.country_name} ({self.total_users} usuarios)"
