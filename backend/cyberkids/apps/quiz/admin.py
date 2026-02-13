from django.contrib import admin
from .models import (
    AudienceSegment, RiskCategory, Quiz, QuizQuestion,
    QuizAlternative, QuizHint, QuizSession, QuizAnswer
)


@admin.register(AudienceSegment)
class AudienceSegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_age', 'max_age', 'display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'segment', 'category', 'difficulty_level', 'base_points', 'is_active']
    list_filter = ['segment', 'category', 'difficulty_level', 'is_active']
    search_fields = ['title', 'description']


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'display_order', 'content_preview', 'points']
    list_filter = ['quiz']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = 'Pregunta'


@admin.register(QuizAlternative)
class QuizAlternativeAdmin(admin.ModelAdmin):
    list_display = ['question', 'display_order', 'content_preview', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:40]
    content_preview.short_description = 'Alternativa'


@admin.register(QuizHint)
class QuizHintAdmin(admin.ModelAdmin):
    list_display = ['question', 'display_order', 'cost_points', 'content_preview']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:40]
    content_preview.short_description = 'Pista'


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'status', 'points_earned', 'hints_used', 'started_at']
    list_filter = ['status', 'quiz', 'started_at']
    search_fields = ['user__username', 'quiz__title']


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'hints_used_count', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['session__user__username']
