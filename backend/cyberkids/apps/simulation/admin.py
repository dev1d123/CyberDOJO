from django.contrib import admin
from .models import Scenario, SensitivePattern, GameSession, ChatMessage


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('scenario_id', 'name', 'threat_type', 'difficulty_level', 'is_active')
    search_fields = ('name', 'description', 'antagonist_goal')
    list_filter = ('threat_type', 'is_active', 'difficulty_level')


@admin.register(SensitivePattern)
class SensitivePatternAdmin(admin.ModelAdmin):
    list_display = ('pattern_id', 'name', 'data_type', 'severity')
    search_fields = ('name', 'regex_pattern', 'data_type')


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'scenario', 'started_at', 'ended_at', 'is_game_over', 'outcome', 'points_awarded')
    search_fields = ('user__username', 'scenario__name', 'outcome', 'game_over_reason')
    list_filter = ('is_game_over', 'outcome', 'points_awarded')
    readonly_fields = ('started_at', 'ended_at')
    raw_id_fields = ('user', 'scenario')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'session', 'role', 'sent_at', 'is_dangerous')
    search_fields = ('content', 'session__session_id')
    list_filter = ('role', 'is_dangerous')
    readonly_fields = ('sent_at',)
from django.contrib import admin

# Register your models here.
