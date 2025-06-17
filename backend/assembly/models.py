from django.db import models
from users.models import Team
from inventory.models import Part

class Aircraft(models.Model):
    class AircraftType(models.TextChoices):
        TB2       = 'TB2',       'TB2'
        TB3       = 'TB3',       'TB3'
        AKINCI    = 'AKINCI',    'Akıncı'
        KIZILELMA = 'KIZILELMA', 'Kızilelma'

    type       = models.CharField(max_length=10, choices=AircraftType.choices)
    created_by = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='aircrafts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} (ID: {self.id})"

class AircraftPart(models.Model):
    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.CASCADE,
        related_name='parts'
    )
    part = models.ForeignKey(Part, on_delete=models.PROTECT)

    class Meta:
        # Aynı part nesnesinin bir uçakta sadece bir kez kullanılması yeterli:
        unique_together = ('aircraft', 'part')

    def __str__(self):
        return f"{self.part} → {self.aircraft}"
