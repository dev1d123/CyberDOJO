from django.contrib import admin

from .models import CyberUser, Country, RiskLevel
admin.site.register(CyberUser)
admin.site.register(Country)
admin.site.register(RiskLevel)
