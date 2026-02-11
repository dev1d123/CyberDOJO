"""
Models for Quiz System (RF-03: Educational Quiz).

Tables:
- audience_segment: Segmentación por edad (6-8, 9-11, etc.)
- risk_category: Categorías temáticas (Phishing, Grooming, etc.)
- quiz: Escenarios de quiz (contenido)
- quiz_question: Preguntas del quiz
- quiz_alternative: Alternativas de respuesta
- quiz_hint: Pistas opcionales
- quiz_session: Sesiones de juego (intentos)
- quiz_answer: Respuestas del usuario
"""

from django.db import models
from apps.cyberUser.models import CyberUser


class AudienceSegment(models.Model):
    """Segmentación de audiencia por edad."""
    segment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # "Niños 6-8", "Niños 9-11"
    description = models.TextField(null=True, blank=True)
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'audience_segment'
        ordering = ['display_order', 'min_age']
        indexes = [
            models.Index(fields=['min_age', 'max_age']),
        ]

    def __str__(self):
        return f"{self.name} ({self.min_age}-{self.max_age} años)"


class RiskCategory(models.Model):
    """Categorías temáticas del quiz."""
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # "Phishing", "Grooming", "Privacidad"
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'risk_category'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Quiz(models.Model):
    """Escenario de quiz (contenido)."""
    quiz_id = models.AutoField(primary_key=True)
    segment = models.ForeignKey(AudienceSegment, on_delete=models.CASCADE, related_name='quizzes')
    category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    difficulty_level = models.IntegerField(default=1)  # 1-5
    base_points = models.IntegerField(default=100)
    time_limit_seconds = models.IntegerField(null=True, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quiz'
        ordering = ['segment', 'category', 'display_order']
        indexes = [
            models.Index(fields=['segment', 'category', 'is_active']),
            models.Index(fields=['display_order']),
        ]

    def __str__(self):
        return f"{self.title} ({self.segment.name})"


class QuizQuestion(models.Model):
    """Preguntas del quiz."""
    question_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    content = models.TextField()
    explanation = models.TextField(null=True, blank=True)
    points = models.IntegerField(default=10)
    display_order = models.IntegerField()
    image_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'quiz_question'
        ordering = ['quiz', 'display_order']
        indexes = [
            models.Index(fields=['quiz', 'display_order']),
        ]

    def __str__(self):
        return f"Q{self.display_order}: {self.content[:50]}"


class QuizAlternative(models.Model):
    """Alternativas de respuesta."""
    alternative_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='alternatives')
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField()  # Feedback específico por alternativa
    display_order = models.IntegerField()

    class Meta:
        db_table = 'quiz_alternative'
        ordering = ['question', 'display_order']
        indexes = [
            models.Index(fields=['question', 'display_order']),
        ]

    def __str__(self):
        correct = "✓" if self.is_correct else "✗"
        return f"{correct} {self.content[:30]}"


class QuizHint(models.Model):
    """Pistas opcionales para preguntas."""
    hint_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='hints')
    content = models.TextField()
    cost_points = models.IntegerField(default=5)  # Costo en puntos
    display_order = models.IntegerField(default=1)

    class Meta:
        db_table = 'quiz_hint'
        ordering = ['question', 'display_order']
        indexes = [
            models.Index(fields=['question', 'display_order']),
        ]

    def __str__(self):
        return f"Pista {self.display_order}: {self.content[:40]}"


class QuizSession(models.Model):
    """Sesiones de juego (intentos)."""
    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='quiz_sessions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='in_progress')  # in_progress, completed, abandoned
    time_spent_seconds = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quiz_session'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'quiz']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} [{self.status}]"


class QuizAnswer(models.Model):
    """Respuestas del usuario."""
    answer_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_alternative = models.ForeignKey(QuizAlternative, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField()
    hints_used_count = models.IntegerField(default=0)  # Pistas usadas en esta pregunta
    answered_at = models.DateTimeField(auto_now_add=True)
    time_spent_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'quiz_answer'
        ordering = ['session', 'answered_at']
        indexes = [
            models.Index(fields=['session', 'question']),
        ]

    def __str__(self):
        correct = "✓" if self.is_correct else "✗"
        return f"{correct} {self.session.user.username} - Q{self.question.display_order}"
