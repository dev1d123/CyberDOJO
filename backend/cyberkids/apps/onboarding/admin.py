from django.contrib import admin
from .models import (
    OnboardingQuestion,
    AnswerOption,
    OnboardingResponse,
    UserStatistic,
    GlobalStatistic
)

admin.site.register(OnboardingQuestion)
admin.site.register(AnswerOption)
admin.site.register(OnboardingResponse)
admin.site.register(UserStatistic)
admin.site.register(GlobalStatistic)