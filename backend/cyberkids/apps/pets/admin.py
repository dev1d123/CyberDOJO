from django.contrib import admin
from .models import Pet, PetState, UserPet

admin.site.register(Pet)
admin.site.register(PetState)
admin.site.register(UserPet)
