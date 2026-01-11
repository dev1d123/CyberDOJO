from rest_framework import serializers
from .models import Minigame, SwipeQuestion, MinigameSession, SwipeResponse


class SwipeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwipeQuestion
        fields = '__all__'


class MinigameSerializer(serializers.ModelSerializer):
    questions = SwipeQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Minigame
        fields = '__all__'


class SwipeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwipeResponse
        fields = '__all__'


class MinigameSessionSerializer(serializers.ModelSerializer):
    responses = SwipeResponseSerializer(many=True, read_only=True)

    class Meta:
        model = MinigameSession
        fields = '__all__'
