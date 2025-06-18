from django.db import models
from django.conf import settings
from django.utils import timezone # tarih için yıl bilgisi lazımdı

class Aircraft(models.Model):
    """
    Monte edilmiş hava araçlarını temsil eder.
    Her yeni uçak, kaydedilirken otomatik bir seri numarası alır.
    """
    class AircraftModel(models.TextChoices):
        TB2 = 'TB2', 'TB2'
        TB3 = 'TB3', 'TB3'
        AKINCI = 'AKINCI', 'Akıncı'
        KIZILELMA = 'KIZILELMA', 'Kızilelma'

    model_name = models.CharField(max_length=10, choices=AircraftModel.choices, verbose_name="Hava Aracı Modeli")
    

    serial_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,     
        editable=False, 
        verbose_name="Seri Numarası"
    )
    
    assembled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assembled_aircrafts")
    assembly_date = models.DateTimeField(auto_now_add=True, verbose_name="Montaj Tarihi")

    def __str__(self):
        return self.serial_number or f"{self.get_model_name_display()} (Kaydedilmedi)"
    
   
    def save(self, *args, **kwargs):
        # Sadece yeni bir nesne oluşturulurken (yani pk yoksa) seri numarası ata
        if not self.pk:
            year = timezone.now().year
            prefix = f"{self.model_name}-{year}"
            
            # Aynı ön eke sahip son uçağı bulup sıradaki numarayı hesapla
            last_aircraft_count = Aircraft.objects.filter(serial_number__startswith=prefix).count()
            next_id = last_aircraft_count + 1
            
            # Seri numarasını formatla (örn: TB2-2025-0001) bu formatı kullanıyorum çok daha uygun olduğunu düşündüm.
            self.serial_number = f"{prefix}-{str(next_id).zfill(4)}"
        
        # Orijinal save metodunu çağırarak nesneyi kaydet
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Hava Aracı"
        verbose_name_plural = "Hava Araçları"
