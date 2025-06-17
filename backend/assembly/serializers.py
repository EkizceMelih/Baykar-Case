# assembly/serializers.py

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from inventory.models import Part
from .models import Aircraft

class AircraftSerializer(serializers.ModelSerializer):
    """
    API üzerinden bir hava aracı oluşturmak için kullanılan serializer.
    Gerekli tüm parçaların ID'lerini alarak montajı gerçekleştirir.
    """
    
    # Yazma işlemi için (örn: POST isteği) parçaların ID'lerini alırız.
    # Bu alan sadece "write-only" olacak, yani uçağı getirirken gösterilmeyecek.
    parts = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.filter(status=Part.Status.AVAILABLE),
        many=True,
        write_only=True, # <-- ÖNEMLİ: Sadece veri gönderirken kullanılır
        label="Parça ID Listesi"
    )

    # Okuma işlemi için (örn: GET isteği) iç içe geçmiş PartSerializer'ı kullanırız.
    # Bu, uçağın detaylarını görüntülerken parçalarının da tüm bilgilerini görmemizi sağlar.
    parts_details = serializers.SerializerMethodField(read_only=True, label="Monte Edilmiş Parçalar")

    class Meta:
        model = Aircraft
        # DEĞİŞTİ: Alanları modelimizle uyumlu hale getirdik. 'type' yerine 'model_name'.
        fields = ['id', 'model_name', 'parts', 'parts_details', 'assembled_by', 'assembly_date']
        read_only_fields = ['id', 'assembly_date', 'assembled_by', 'parts_details']

    def get_parts_details(self, obj):
        """
        Bir Aircraft nesnesine bağlı olan parçaların detaylarını getiren metod.
        Modeldeki related_name='parts' sayesinde `obj.parts.all()` çalışır.
        """
        from inventory.serializers import PartSerializer # Döngüsel importu önlemek için burada import ediyoruz
        return PartSerializer(obj.parts.all(), many=True).data

    def validate(self, data):
        """
        Montaj işlemi için gönderilen verilerin iş kurallarına uygunluğunu kontrol eder.
        """
        user = self.context['request'].user
        
        # 1) Sadece Montaj Takımı uçak üretebilir.
        # Not: User modelinizde 'team' ilişkisi ve Team modelinde 'name' alanı olmalı.
        if not hasattr(user, 'team') or user.team.name != 'MONTAJ':
            raise PermissionDenied("Sadece MONTAJ takımı uçak üretebilir.")

        parts = data.get('parts', [])
        plane_model_name = data.get('model_name')

        if not parts:
            raise ValidationError("Montaj için en az bir parça gönderilmelidir.")

        # 2) Tüm parçalar, oluşturulacak uçağın modeline uygun mu?
        for part in parts:
            if part.aircraft_model != plane_model_name:
                raise ValidationError(
                    f"Parça #{part.id} ({part.get_type_display()}) {plane_model_name} uçağına uygun değil."
                )

        # 3) Uçak montajı için gereken tüm parça tipleri (KANAT, GOVDE vb.) gönderilmiş mi?
        required_part_types = {choice[0] for choice in Part.PartType.choices}
        provided_part_types = {part.type for part in parts}
        
        if len(required_part_types) != len(provided_part_types):
             missing = required_part_types - provided_part_types
             if missing:
                 # `Part.PartType.labels` Django'nun standart özelliğidir.
                 missing_names = ", ".join([Part.PartType(m).label for m in missing])
                 raise ValidationError(f"Eksik parça tipleri: {missing_names}.")

        return data

    def create(self, validated_data):
        """
        Validasyondan geçen verilerle uçağı oluşturur ve parçaları ilişkilendirir.
        """
        # 'parts' listesini asıl veri kümesinden ayırıyoruz, çünkü bu Aircraft modelinin doğrudan bir alanı değil.
        parts_to_assemble = validated_data.pop('parts')
        user = self.context['request'].user

        # 4) Uçağı oluştur
        # validated_data içinde sadece 'model_name' kaldı.
        aircraft = Aircraft.objects.create(
            assembled_by=user,
            **validated_data
        )

        # 5) Parçaları uçağa bağla ve durumlarını güncelle (Artık AircraftPart yok!)
        for part in parts_to_assemble:
            part.used_in_aircraft = aircraft  # <-- İLİŞKİ BURADA KURULUYOR!
            part.status = Part.Status.USED  # <-- Parçanın durumu 'Kullanıldı' olarak değişiyor.
            part.save(update_fields=['used_in_aircraft', 'status'])

        return aircraft