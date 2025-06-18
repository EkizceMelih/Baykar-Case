from rest_framework import serializers
from .models import Part
from users.models import Team 

class PartSerializer(serializers.ModelSerializer):
    """
    Parça modelini API için JSON formatına çevirir.
    - Okunabilirliği artırmak için ek alanlar içerir.
    - Parça oluşturma işlemi için iş kurallarını (validasyon) uygular.
    """
  
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    aircraft_model_display = serializers.CharField(source='get_aircraft_model_display', read_only=True)

    class Meta:
        model = Part
        # API'de gösterilecek ve kullanılacak tüm alanların listesi
        fields = [
            'id', 
            'serial_number', 
            'type', 
            'type_display',
            'aircraft_model',
            'aircraft_model_display',
            'status', 
            'status_display',
            'created_by', 
            'created_by_username', 
            'created_at',
            'used_in_aircraft'
        ]
        # Bu alanlar sistem tarafından yönetilir, kullanıcı tarafından gönderilemez/değiştirilemez.
        read_only_fields = (
            'id', 'serial_number', 'status', 'created_by', 'created_at', 'used_in_aircraft', 
            'type_display', 'status_display', 'aircraft_model_display', 'created_by_username'
        )

    def validate(self, data):
        """
        Veri kaydedilmeden önce çalışır ve iş kurallarını kontrol eder.
        Bu metod, validasyon için en doğru yerdir.
        """
        user = self.context['request'].user
        
        #  Kullanıcının bir takımı olmalı
        if not hasattr(user, 'team') or not user.team:
            raise serializers.ValidationError("Parça oluşturmak için bir takıma ait olmalısınız.")
        
        #  Montaj Takımı'nın parça üretmesini engelle
        if user.team.type == Team.TeamType.MONTAJ:
            raise serializers.ValidationError("Montaj Takımı yeni parça üretemez.")

        #  Takımların sadece kendi tipinde parça üretmesini sağla
        team_type = user.team.type
        part_type_to_create = data.get('type')
        if part_type_to_create != team_type:
             raise serializers.ValidationError(f'Takımınız sadece "{team_type}" tipinde parça üretebilir.')

        return data
    
    def create(self, validated_data):
        """
        Validasyondan geçen verilerle yeni bir parça nesnesi oluşturur.
        """
        # created_by ve status alanlarını sistem otomatik olarak ayarlar.
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = Part.Status.AVAILABLE
        
        # Not: Seri numarası, Part modelinin save() metodunda otomatik olarak oluşturulacaktır.
        return super().create(validated_data)
