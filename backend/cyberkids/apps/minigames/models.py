from django.db import models
from apps.cyberUser.models import CyberUser, Country


class Minigame(models.Model):
    minigame_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # swipe, quiz, memory
    description = models.TextField(null=True, blank=True)
    base_points = models.IntegerField(default=50)
    time_limit_sec = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'minigame'

    def __str__(self):
        return self.name


class SwipeQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    minigame = models.ForeignKey(Minigame, on_delete=models.CASCADE, related_name='questions')
    notification_content = models.TextField()
    correct_answer = models.CharField(max_length=20)  # Safe, Dangerous
    explanation = models.TextField(null=True, blank=True)
    difficulty_level = models.IntegerField(default=1)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='swipe_questions')

    class Meta:
        db_table = 'swipe_question'

    def __str__(self):
        return f"{self.minigame.name} - Q{self.question_id}"


class MinigameSession(models.Model):
    minigame_session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='minigame_sessions')
    minigame = models.ForeignKey(Minigame, on_delete=models.CASCADE, related_name='sessions')
    played_at = models.DateTimeField(auto_now_add=True)
    points_earned = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    time_spent_sec = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'minigame_session'

    def __str__(self):
        return f"{self.user.username} - {self.minigame.name}"


class SwipeResponse(models.Model):
    response_id = models.AutoField(primary_key=True)
    minigame_session = models.ForeignKey(MinigameSession, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(SwipeQuestion, on_delete=models.CASCADE, related_name='responses')
    user_answer = models.CharField(max_length=20)
    is_correct = models.BooleanField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'swipe_response'

    def __str__(self):
        return f"Session {self.minigame_session_id} - Q{self.question_id}"
