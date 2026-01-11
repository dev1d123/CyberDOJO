from django.contrib import admin
from .models import Minigame, SwipeQuestion, MinigameSession, SwipeResponse

admin.site.register(Minigame)
admin.site.register(SwipeQuestion)
admin.site.register(MinigameSession)
admin.site.register(SwipeResponse)
