from rest_framework import viewsets, permissions
from .models import Aircraft
from .serializers import AircraftSerializer

class AircraftViewSet(viewsets.ModelViewSet):
    serializer_class = AircraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Sadece Montaj Takımı tüm uçakları listeleyebilir
        if self.request.user.team.name == 'Montaj Takımı':
            return Aircraft.objects.all()
        # Diğer takımlar hiçbir uçak görmesin
        return Aircraft.objects.none()
