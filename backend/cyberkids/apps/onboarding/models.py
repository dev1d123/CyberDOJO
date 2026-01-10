from django.db import models
from apps.cyberUser.models import CyberUser, Country


class OnboardingQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    content = models.TextField()
    response_type = models.CharField(max_length=50)  # multiple_choice, yes_no, scale
    risk_weight = models.IntegerField(default=1)
    display_order = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'onboarding_question'

    def __str__(self):
        return f"Q{self.display_order}: {self.content[:50]}"


class AnswerOption(models.Model):
    option_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(OnboardingQuestion, on_delete=models.CASCADE, related_name='options')
    content = models.TextField()
    risk_value = models.IntegerField()
    display_order = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'answer_option'

    def __str__(self):
        return f"{self.question.question_id} - {self.content[:30]}"


class OnboardingResponse(models.Model):
    response_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='onboarding_responses')
    question = models.ForeignKey(OnboardingQuestion, on_delete=models.CASCADE, related_name='responses')
    option = models.ForeignKey(AnswerOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='responses')
    open_answer = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'onboarding_response'
        unique_together = ['user', 'question']

    def __str__(self):
        return f"User {self.user.username} - Q{self.question.question_id}"


class UserStatistic(models.Model):
    statistic_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='statistics')
    metric = models.CharField(max_length=100)  
    value = models.FloatField()
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_statistic'

    def __str__(self):
        return f"{self.user.username} - {self.metric}: {self.value}"


class GlobalStatistic(models.Model):
    statistic_id = models.AutoField(primary_key=True)
    metric = models.CharField(max_length=100)
    value = models.FloatField()
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='statistics')
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'global_statistic'

    def __str__(self):
        country_name = self.country.name if self.country else "Global"
        return f"{country_name} - {self.metric}: {self.value}"
