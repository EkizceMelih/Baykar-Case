from django.db import models
from django.contrib.auth.models import AbstractUser

class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='members',
        null=True,
        blank=True
    )
