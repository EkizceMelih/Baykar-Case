# backend/inventory/serializers.py

from rest_framework import serializers
from .models import Part

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = (
            'id',
            'type',
            'aircraft_type',
            'status',
            'created_by',
            'created_at',
        )
        read_only_fields = ('id', 'status', 'created_by', 'created_at')

    def create(self, validated_data):
        # request.user’ı context'ten alıp created_by ve status ekleyelim
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['status'] = Part.Status.AVAILABLE
        return super().create(validated_data)
