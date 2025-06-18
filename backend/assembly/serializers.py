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
    
  
    parts = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.filter(status=Part.Status.AVAILABLE),
        many=True,
        write_only=True,
        label="Parça ID Listesi"
    )


    # Bu, uçağın detaylarını görüntülerken parçalarının da tüm bilgilerini görmemizi sağlar.
    parts_details = serializers.SerializerMethodField(read_only=True, label="Monte Edilmiş Parçalar")

    class Meta:
        model = Aircraft
     
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
        
        # Sadece Montaj Takımı uçak üretebilir bu yüzden burası gerekli
       
        if not hasattr(user, 'team') or user.team.name != 'MONTAJ':
            raise PermissionDenied("Sadece MONTAJ takımı uçak üretebilir.")

        parts = data.get('parts', [])
        plane_model_name = data.get('model_name')

        if not parts:
            raise ValidationError("Montaj için en az bir parça gönderilmelidir.")

        # Tüm parçalar, oluşturulacak uçağın modeline uygun mu. TB3, TB2 parçaları ayrı örneğin
        for part in parts:
            if part.aircraft_model != plane_model_name:
                raise ValidationError(
                    f"Parça #{part.id} ({part.get_type_display()}) {plane_model_name} uçağına uygun değil."
                )

        #  Uçak montajı için gereken tüm parça tipleri
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

        # 4) Uçak oluşturma alanı
      
        aircraft = Aircraft.objects.create(
            assembled_by=user,
            **validated_data
        )

        # 5) Parçaları uçağa bağla ve durumlarını güncelle 
        for part in parts_to_assemble:
            part.used_in_aircraft = aircraft  # relation kuruyorum
            part.status = Part.Status.USED  # <-- parça kullanıldı olarak değişiyor ve stoktan düşüyor müsait olanlardan
            part.save(update_fields=['used_in_aircraft', 'status'])

        return aircraft