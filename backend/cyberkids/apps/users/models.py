from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    country_id = models.IntegerField(null=True, blank=True)
    risk_level_id = models.IntegerField(null=True, blank=True)
    pet_id = models.IntegerField(null=True, blank=True)
    cybercreds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
