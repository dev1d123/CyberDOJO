from rest_framework import serializers
from .models import GameSession, ChatMessage, Scenario, SensitivePattern


class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['session_id', 'user', 'scenario', 'started_at', 'ended_at', 'status', 'points_earned', 'is_game_over', 'game_over_reason']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message_id', 'session', 'role', 'content', 'sent_at', 'is_dangerous', 'detected_pattern']


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['scenario_id', 'name', 'description', 'antagonist_goal', 'difficulty_level', 'base_points', 'threat_type', 'is_active']


class SensitivePatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensitivePattern
        fields = ['pattern_id', 'name', 'regex_pattern', 'data_type', 'alert_message', 'severity']
from rest_framework import serializers

