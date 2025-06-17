# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class Team(models.Model):
    class TeamType(models.TextChoices):
        KANAT = "KANAT", "Kanat Takımı"
        GOVDE = "GOVDE", "Gövde Takımı"
        KUYRUK = "KUYRUK", "Kuyruk Takımı"
        AVIYONIK = "AVIYONIK", "Aviyonik Takımı"
        MONTAJ = "MONTAJ", "Montaj Takımı"

    name = models.CharField(max_length=100, unique=True, verbose_name="Takım Adı")
    type = models.CharField(
        max_length=10,
        choices=TeamType.choices,
        verbose_name="Takım Tipi",
        default=TeamType.KANAT  # <-- BU SATIRI EKLEYİN!
    )

    def __str__(self):
        return self.name

class User(AbstractUser):
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name="Takım"
    )