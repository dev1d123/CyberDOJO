from django.contrib import admin

from .models import CyberUser, Country, RiskLevel, Preferences
admin.site.register(CyberUser)
admin.site.register(Country)
admin.site.register(RiskLevel)
admin.site.register(Preferences)
