from rest_framework import serializers
from .models import ProgressionLevel, CosmeticItem, UserInventory, CreditTransaction, UserProgress, Achievement, UserAchievement


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


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='achievement.name', read_only=True)
    achievement_description = serializers.CharField(source='achievement.description', read_only=True)
    achievement_category = serializers.CharField(source='achievement.category', read_only=True)
    achievement_icon = serializers.SerializerMethodField()
    cybercreds_reward = serializers.IntegerField(source='achievement.cybercreds_reward', read_only=True)
    xp_reward = serializers.IntegerField(source='achievement.xp_reward', read_only=True)
    requirement_value = serializers.IntegerField(source='achievement.requirement_value', read_only=True)
    is_hidden = serializers.BooleanField(source='achievement.is_hidden', read_only=True)

    class Meta:
        model = UserAchievement
        fields = [
            'user_achievement_id', 'user', 'achievement', 'unlocked_at', 
            'progress', 'is_claimed', 'achievement_name', 'achievement_description',
            'achievement_category', 'achievement_icon', 'cybercreds_reward', 
            'xp_reward', 'requirement_value', 'is_hidden'
        ]

    def get_achievement_icon(self, obj):
        if obj.achievement.icon:
            return obj.achievement.icon.url
        return None


class UserAchievementDetailSerializer(serializers.Serializer):
    """Serializer para mostrar logros con su estado de desbloqueo."""
    achievement_id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    icon = serializers.SerializerMethodField()
    cybercreds_reward = serializers.IntegerField()
    xp_reward = serializers.IntegerField()
    requirement_type = serializers.CharField()
    requirement_value = serializers.IntegerField()
    is_hidden = serializers.BooleanField()
    is_unlocked = serializers.BooleanField()
    progress = serializers.IntegerField()
    unlocked_at = serializers.DateTimeField(allow_null=True)
    is_claimed = serializers.BooleanField()

    def get_icon(self, obj):
        if isinstance(obj, dict):
            icon = obj.get('icon')
            if icon:
                return icon.url if hasattr(icon, 'url') else icon
        return None
