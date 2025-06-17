# assembly/admin.py

from django.contrib import admin
from .models import Aircraft

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    """
    Aircraft modeli için admin paneli ayarları.
    """
    # DEĞİŞTİ: Alan isimleri modeldeki yeni isimlerle güncellendi.
    list_display = ('serial_number', 'model_name', 'assembled_by', 'assembly_date')
    list_filter = ('model_name', 'assembled_by', 'assembly_date')
    search_fields = ('serial_number', 'model_name')
    readonly_fields = ('assembly_date',) # Otomatik oluşturulan alanlar sadece okunabilir olsun

# Eski admin.site.register(Aircraft) satırını bu class yapısı
# ile değiştirmek daha modern ve esnek bir yöntemdir.