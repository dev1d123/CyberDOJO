from rest_framework import serializers
from .models import ProgressionLevel, CosmeticItem, UserInventory, CreditTransaction, UserProgress


class ProgressionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressionLevel
        fields = '__all__'


class CosmeticItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CosmeticItem
        fields = '__all__'


class UserInventorySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_type = serializers.CharField(source='item.type', read_only=True)

    class Meta:
        model = UserInventory
        fields = '__all__'


class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = '__all__'


class UserProgressSerializer(serializers.ModelSerializer):
    level_number = serializers.IntegerField(source='current_level.level_number', read_only=True)
    level_name = serializers.CharField(source='current_level.name', read_only=True)

    class Meta:
        model = UserProgress
        fields = '__all__'
