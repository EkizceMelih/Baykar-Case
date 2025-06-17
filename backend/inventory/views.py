# backend/inventory/views.py

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Part
from .serializers import PartSerializer

class PartViewSet(viewsets.ModelViewSet):
    serializer_class   = PartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        team_label = self.request.user.team.name.split()[0].upper()
        return Part.objects.filter(type=team_label)

    def perform_create(self, serializer):
        user       = self.request.user
        team_label = user.team.name.split()[0].upper()
        ptype      = serializer.validated_data.get('type')

        if ptype != team_label:
            raise PermissionDenied(
                f"{team_label.title()} takımı yalnızca {team_label.title()} parçası üretebilir."
            )

        # artık extra argüman yok:
        serializer.save()
