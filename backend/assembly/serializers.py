from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from inventory.models import Part
from .models import Aircraft, AircraftPart

class AircraftSerializer(serializers.ModelSerializer):
    # Gelen parça ID’leri, yalnızca AVAILABLE ve doğru uçak tipindeki parçalar olmalı
    parts = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.filter(status='AVAILABLE'),
        many=True
    )

    class Meta:
        model = Aircraft
        fields = ['id', 'type', 'parts', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        # 1) Sadece Montaj Takımı uçak üretebilir
        if user.team.name != 'Montaj Takımı':
            raise PermissionDenied("Sadece Montaj Takımı uçak üretebilir.")

        parts = data['parts']
        plane_type = data['type']

        # 2) Tüm parçalar plane_type’a ait mi?
        for p in parts:
            if p.aircraft_type != plane_type:
                raise ValidationError(f"Parça #{p.id} ({p.get_type_display()}) {plane_type} uçağına uygun değil.")

        # 3) Gereken tüm parça tipleri gelmiş mi?
        required = {t[0] for t in Part.PartType.choices}
        provided = {p.type for p in parts}
        missing = required - provided
        if missing:
            missing_names = ", ".join(Part.PartType.labels_by_value()[m] for m in missing)
            raise ValidationError(f"Eksik parça tipleri: {missing_names}.")

        return data

    def create(self, validated_data):
        parts = validated_data.pop('parts')
        user_team = self.context['request'].user.team

        # 4) Uçağı oluştur ve parçaları ilişkilendir
        aircraft = Aircraft.objects.create(
            type=validated_data['type'],
            created_by=user_team
        )
        for p in parts:
            AircraftPart.objects.create(aircraft=aircraft, part=p)
            p.status = Part.PartStatus.ALLOCATED  # veya 'ALLOCATED'
            p.save()

        return aircraft
