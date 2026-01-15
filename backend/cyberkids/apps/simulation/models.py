"""
Models for RF-02: Social Engineering Simulation.

Tables:
- scenario: Simulation scenarios with antagonist goals and threat types
- sensitive_pattern: Regex patterns to detect sensitive data disclosure
- game_session: User game sessions tracking progress and status
- chat_message: Chat messages between user and AI antagonist
"""

from django.db import models
from apps.cyberUser.models import CyberUser, Country


class Scenario(models.Model):
	scenario_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True, blank=True)
	antagonist_goal = models.CharField(max_length=100)
	difficulty_level = models.IntegerField()
	base_points = models.IntegerField(default=100)
	threat_type = models.CharField(max_length=50, null=True, blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		db_table = 'scenario'

	def __str__(self):
		return self.name


class SensitivePattern(models.Model):
	pattern_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	regex_pattern = models.CharField(max_length=500)
	data_type = models.CharField(max_length=50)
	alert_message = models.CharField(max_length=255, null=True, blank=True)
	severity = models.IntegerField(default=1)

	class Meta:
		db_table = 'sensitive_pattern'

	def __str__(self):
		return f"{self.name} ({self.data_type})"


class GameSession(models.Model):
	session_id = models.AutoField(primary_key=True)
	user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='game_sessions')
	scenario = models.ForeignKey(Scenario, on_delete=models.SET_NULL, null=True, related_name='sessions')
	started_at = models.DateTimeField(auto_now_add=True)
	ended_at = models.DateTimeField(null=True, blank=True)
	status = models.CharField(max_length=20, default='in_progress')
	points_earned = models.IntegerField(default=0)
	# Número de intentos que ha hecho el antagonista para obtener el objetivo
	antagonist_attempts = models.IntegerField(default=0)
	# Indicador para evitar recompensar puntos más de una vez
	points_awarded = models.BooleanField(default=False)
	# Snapshot del escenario asignado (JSON) para auditoría/reproducción
	scenario_snapshot = models.JSONField(null=True, blank=True)

	# Resultado final de la sesión: 'won' (superado), 'failed' (fallado), 'abandoned' (abandonado)
	# Se mantiene `is_game_over` como indicador booleano de que la sesión terminó.
	outcome = models.CharField(max_length=20, null=True, blank=True)
	# `is_game_over` ahora es Nullable:
	#   - None => la sesión está en curso (in progress)
	#   - True => la sesión terminó y el usuario PERDIÓ
	#   - False => la sesión terminó y el usuario GANÓ
	# Esto evita invertir la semántica y hace explícito el estado "en curso".
	is_game_over = models.BooleanField(null=True, blank=True)
	game_over_reason = models.CharField(max_length=255, null=True, blank=True)

	class Meta:
		db_table = 'game_session'
		indexes = [
			models.Index(fields=['user']),
			models.Index(fields=['started_at']),
		]

	def __str__(self):
		return f"Session {self.session_id} - {self.user.username}"


class ChatMessage(models.Model):
	message_id = models.AutoField(primary_key=True)
	session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='messages')
	role = models.CharField(max_length=20)  # user, antagonist, system
	content = models.TextField()
	sent_at = models.DateTimeField(auto_now_add=True)
	is_dangerous = models.BooleanField(default=False)
	detected_pattern = models.ForeignKey(SensitivePattern, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')

	class Meta:
		db_table = 'chat_message'
		indexes = [models.Index(fields=['session'])]

	def __str__(self):
		return f"{self.role} @ {self.sent_at}: {self.content[:40]}"
