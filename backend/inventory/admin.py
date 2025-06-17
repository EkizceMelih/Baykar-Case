from django.contrib import admin
from .models import Part

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    """
    Part modeli için admin paneli ayarları.
    Bu sınıf, parça listesinin nasıl görüneceğini ve filtreleneceğini özelleştirir.
    """
    
    # Parça listesinde hangi kolonların görüneceğini belirler.
    list_display = (
        'serial_number', 
        'type', 
        'aircraft_model', 
        'status', 
        'created_by', 
        'created_at'
    )
    
    # Sağ tarafa, duruma, tipe veya modele göre filtreleme yapabileceğiniz bir menü ekler.
    list_filter = ('status', 'type', 'aircraft_model')
    
    # Listenin üzerine, seri numarasına veya oluşturan kullanıcı adına göre arama yapabileceğiniz bir arama kutusu ekler.
    search_fields = ('serial_number', 'created_by__username')
    
    # Sayfa başına gösterilecek nesne sayısı.
    list_per_page = 25

    # Alanları gruplamak için (isteğe bağlı ama düzenli gösterir)
    fieldsets = (
        ('Parça Bilgileri', {
            'fields': ('serial_number', 'type', 'aircraft_model', 'status')
        }),
        ('Kullanım Bilgileri', {
            'fields': ('used_in_aircraft',)
        }),
        ('Kayıt Bilgileri', {
            'fields': ('created_by', 'created_at')
        }),
    )
    
    # Otomatik oluşturulan alanların sadece okunabilir olmasını sağlar.
    readonly_fields = ('serial_number', 'created_at')