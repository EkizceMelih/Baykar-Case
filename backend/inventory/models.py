from django.db import models
from django.conf import settings

class Part(models.Model):
    class PartType(models.TextChoices):
        KANAT   = "KANAT",   "Kanat"
        GOVDE   = "GOVDE",   "Gövde"
        KUYRUK  = "KUYRUK",  "Kuyruk"
        AVIYONIK= "AVIYONIK","Aviyonik"

    class AircraftType(models.TextChoices):
        TB2      = "TB2",      "TB2"
        TB3      = "TB3",      "TB3"
        AKINCI   = "AKINCI",   "AKINCI"
        KIZILELMA= "KIZILELMA","KIZILELMA"

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Stokta"
        RECYCLED  = "RECYCLED",  "Geri Dönüşüme"
        ALLOCATED = "ALLOCATED", "Tahsisli"

    type           = models.CharField(max_length=10, choices=PartType.choices)
    aircraft_type  = models.CharField(max_length=10, choices=AircraftType.choices)
    status         = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} ({self.aircraft_type})"
