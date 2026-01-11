from django.db import models
from apps.cyberUser.models import CyberUser
from cloudinary.models import CloudinaryField

class Pet(models.Model):
    pet_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    base_sprite = CloudinaryField('image', folder='pets/sprites/', null=True, blank=True)
    cybercreds_cost = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'pet'

    def __str__(self):
        return self.name

# Saved a different animation for each state of the pet
class PetState(models.Model):
    state_id = models.AutoField(primary_key=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='states')
    state_name = models.CharField(max_length=50)  # Error, Success, Thinking, Idle
    svg = CloudinaryField('svg', folder='pets/states/', null=True, blank=True)
    animation_url = CloudinaryField('animation', folder='pets/animations/', null=True, blank=True)
    duration_ms = models.IntegerField(default=500)

    class Meta:
        db_table = 'pet_state'

    def __str__(self):
        return f"{self.pet.name} - {self.state_name}"

# User's owned pets
class UserPet(models.Model):
    user_pet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CyberUser, on_delete=models.CASCADE, related_name='pets')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='owners')
    is_equipped = models.BooleanField(default=False)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_pet'
        unique_together = ['user', 'pet']

    def __str__(self):
        return f"{self.user.username} - {self.pet.name}"
