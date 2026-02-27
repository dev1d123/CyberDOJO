from django.contrib import admin
from .models import ProgressionLevel, CosmeticItem, UserInventory, CreditTransaction, UserProgress, Achievement, UserAchievement


admin.site.register(ProgressionLevel)
admin.site.register(CosmeticItem)
admin.site.register(UserInventory)
admin.site.register(CreditTransaction)
admin.site.register(UserProgress)
admin.site.register(Achievement)
admin.site.register(UserAchievement)