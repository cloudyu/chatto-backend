from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    username = models.CharField(max_length=256, unique=True)
    email = models.CharField(max_length=256)
    avatar = models.CharField(max_length=256)
    roles = models.CharField(max_length=256, default='')

    def __str__(self):
        return str(self.username)
