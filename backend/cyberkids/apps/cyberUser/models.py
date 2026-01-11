from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from cloudinary.models import CloudinaryField

class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=10)
    language = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'country'

    def __str__(self):
        return self.name


class RiskLevel(models.Model):
    risk_level_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    ai_difficult = models.IntegerField()
    points_multiplier = models.FloatField()

    class Meta:
        db_table = 'risk_level'

    def __str__(self):
        return self.name


class CyberUserManager(models.Manager):
    
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = email.lower().strip()
        
        preferences = Preferences.objects.create(
            receive_newsletters=False,
            dark_mode=False
        )
        
        user = self.model(email=email, username=username, preferences=preferences, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
class Preferences(models.Model):
    preference_id = models.AutoField(primary_key=True)
    receive_newsletters = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)
    base_content = models.TextField(null=True, blank=True)
    tone_instructions = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'preferences'

    def __str__(self):
        return f"Preferences for {self.cyberuser.username}"

class CyberUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    pet_id = models.IntegerField(null=True, blank=True)
    cybercreds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    avatar = CloudinaryField('avatar', folder='avatars/', null=True, blank=True, default='avatars/default.jpg')
    preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    risk_level = models.ForeignKey(RiskLevel, on_delete=models.CASCADE, null=True, blank=True, related_name='users')

    objects = CyberUserManager()

    class Meta:
        db_table = 'cyber_user'

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)