from rest_framework import serializers
from .models import OnboardingQuestion, AnswerOption, OnboardingResponse, UserStatistic, GlobalStatistic


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = '__all__'


class OnboardingQuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = OnboardingQuestion
        fields = '__all__'


class OnboardingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingResponse
        fields = '__all__'


class UserStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistic
        fields = '__all__'


class GlobalStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalStatistic
        fields = '__all__'
