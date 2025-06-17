# inventory/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone # <-- Yıl bilgisi için eklendi

class Part(models.Model):
    # ... (PartType, AircraftModel, Status sınıfları aynı kalacak) ...
    class PartType(models.TextChoices):
        KANAT = "KANAT", "Kanat"
        GOVDE = "GOVDE", "Gövde"
        KUYRUK = "KUYRUK", "Kuyruk"
        AVIYONIK = "AVIYONIK", "Aviyonik"
    
    class AircraftModel(models.TextChoices):
        TB2 = 'TB2', 'TB2'
        TB3 = 'TB3', 'TB3'
        AKINCI = 'AKINCI', 'Akıncı'
        KIZILELMA = 'KIZILELMA', 'Kızilelma'

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Mevcut"
        USED = "USED", "Kullanıldı"
        RECYCLED = "RECYCLED", "Geri Dönüşümde"

    type = models.CharField(max_length=10, choices=PartType.choices, verbose_name="Parça Tipi")
    aircraft_model = models.CharField(max_length=10, choices=AircraftModel.choices, verbose_name="Uyumlu Hava Aracı Modeli")
    
    # --- DEĞİŞTİ: Artık kullanıcı tarafından düzenlenemez ve boş olabilir ---
    serial_number = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True, # <-- Kaydetme anında oluşturulacağı için geçici olarak boş olabilir
        editable=False, # <-- Admin panelinde ve formlarda bu alanın görünmesini engeller
        verbose_name="Seri Numarası"
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, verbose_name="Durum")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_parts")
    created_at = models.DateTimeField(auto_now_add=True)
    used_in_aircraft = models.ForeignKey('assembly.Aircraft', null=True, blank=True, on_delete=models.SET_NULL, related_name="parts")

    def __str__(self):
        # Seri numarası oluştuysa onu göstermek daha mantıklı
        return self.serial_number or f"{self.aircraft_model} - {self.get_type_display()} (Henüz kaydedilmedi)"

    # --- YENİ: Otomatik seri numarası oluşturma mantığı ---
    def save(self, *args, **kwargs):
        # Eğer bu yeni bir nesne ise (yani henüz bir primary key'i yoksa)
        # ve seri numarası henüz atanmamışsa...
        if not self.pk and not self.serial_number:
            # Parça tipi, modeli ve yılına göre bir ön ek oluştur
            year = timezone.now().year
            prefix = f"{self.type}-{self.aircraft_model}-{year}"
            
            # Aynı ön eke sahip son parçayı bulup sıradaki numarayı hesapla
            last_part_count = Part.objects.filter(serial_number__startswith=prefix).count()
            next_id = last_part_count + 1
            
            # Seri numarasını oluştur (örn: KANAT-AKINCI-2025-0001)
            self.serial_number = f"{prefix}-{str(next_id).zfill(4)}"

        # Orijinal save metodunu çağırarak nesneyi veritabanına kaydet
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Parça"
        verbose_name_plural = "Parçalar"