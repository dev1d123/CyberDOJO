from django.db import models
from apps.cyberUser.models import CyberUser
from cloudinary.models import CloudinaryField


class ProgressionLevel(models.Model):
    level_id = models.AutoField(primary_key=True)
    level_number = models.IntegerField(unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    required_xp = models.IntegerField()
    cybercreds_reward = models.IntegerField(default=0)
    badge = CloudinaryField('badge', folder='progression/badges/', null=True, blank=True)

    class Meta:
        db_table = 'progression_level'

    def __str__(self):
        return f"Level {self.level_number}: {self.name}"


class CosmeticItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # avatar, frame, background, effect
    description = models.CharField(max_length=255, null=True, blank=True)
    image = CloudinaryField('image', folder='cosmetic_items/', null=True, blank=True)
    cybercreds_cost = models.IntegerField()
    required_level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cosmetic_item'

    def __str__(self):
        return f"{self.name} ({self.type})"


class UserInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(CosmeticItem, on_delete=models.CASCADE, related_name='owners')
    acquired_at = models.DateTimeField(auto_now_add=True)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_inventory'
        unique_together = ['user', 'item']

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"


class CreditTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()  # Positive=earn, Negative=spend
    transaction_type = models.CharField(max_length=50)  # game, minigame, purchase, bonus
    description = models.CharField(max_length=255, null=True, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    reference_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'credit_transaction'

    def __str__(self):
        return f"{self.user.username}: {self.amount} ({self.transaction_type})"


class UserProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CyberUser, on_delete=models.CASCADE, related_name='progress')
    current_level = models.ForeignKey(ProgressionLevel, on_delete=models.SET_NULL, null=True)
    current_xp = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_progress'

    def __str__(self):
        return f"{self.user.username} - Level {self.current_level.level_number if self.current_level else 0}"
