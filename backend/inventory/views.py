from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count

# Diğer uygulamalardan ve kütüphanelerden importlar
from .models import Part
from .forms import PartForm
from users.models import Team

# DRF için importlar
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import PartSerializer


@login_required
def part_list(request):
    """
    Kullanıcının takımına göre ilgili sayfayı gösterir.
    - Montaj Takımı ise: Genel envanter durumunu gösteren bir 'dashboard'a yönlendirilir.
    - Diğer takımlar ise: Kendi ürettikleri parçaların listesini görürler.
    """
    user = request.user
    if not hasattr(user, 'team') or not user.team:
        return HttpResponseForbidden("Bir takıma ait olmalısınız!")

    # DEĞİŞİKLİK: Kullanıcının takım tipini kontrol et
    if user.team.type == Team.TeamType.MONTAJ:
        # --- EĞER KULLANICI MONTAJ TAKIMINDANSA ---
        from assembly.models import Aircraft  # Döngüsel importu önlemek için burada import ediyoruz

        # Stoktaki tüm parçaları, uçak modeline ve parça tipine göre sayalım
        part_counts = Part.objects.filter(status='AVAILABLE').values(
            'aircraft_model', 
            'type'
        ).annotate(
            count=Count('id')
        ).order_by('aircraft_model', 'type')
        
        # Veriyi şablonda kolay kullanmak için bir sözlük yapısına çevirelim
        inventory_summary = {}
        for item in part_counts:
            model = item['aircraft_model']
            if model not in inventory_summary:
                inventory_summary[model] = {}
            inventory_summary[model][item['type']] = item['count']

        context = {
            'inventory_summary': inventory_summary,
            'part_types': Part.PartType.choices,
            'aircraft_models': Aircraft.AircraftModel.choices,
        }
        # Onu, özel "montaj gösterge paneli" şablonuna yönlendir
        return render(request, "inventory/assembly_dashboard.html", context)
    else:
        # --- DİĞER TAKIMLAR İÇİN ESKİ MANTIK DEVAM EDİYOR ---
        team_type = user.team.type
        parts = Part.objects.filter(type=team_type, status=Part.Status.AVAILABLE)
        context = {'parts': parts}
        return render(request, "inventory/part_list.html", context)


@login_required
def add_part(request):
    user = request.user
    if not hasattr(user, 'team') or not user.team:
        return HttpResponseForbidden("Parça eklemek için bir takıma ait olmalısınız!")
    
    if user.team.type == Team.TeamType.MONTAJ:
        return HttpResponseForbidden("Montaj takımı yeni parça üretemez!")

    team_type = user.team.type

    if request.method == "POST":
        form = PartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.created_by = user
            
            if part.type != team_type:
                form.add_error('type', f'Takımınız sadece "{team_type}" tipinde parça üretebilir.')
                return render(request, "inventory/add_part.html", {"form": form})

            part.save()
            return redirect("part-list")
    else:
        form = PartForm()
        form.fields['type'].initial = team_type
        form.fields['type'].widget.attrs['readonly'] = True
        
    return render(request, "inventory/add_part.html", {"form": form})


@login_required
def recycle_part(request, part_id):
    part = get_object_or_404(Part, pk=part_id)
    user_team_type = request.user.team.type

    # Sadece montaj takımı olmayanlar ve parçanın sahibi olan takım silebilir
    if user_team_type == Team.TeamType.MONTAJ or part.type != user_team_type:
        return HttpResponseForbidden("Bu parçayı geri dönüşüme gönderme yetkiniz yok.")

    if part.status == Part.Status.AVAILABLE:
        part.status = Part.Status.RECYCLED
        part.save()
    return redirect("part-list")


# =======================================================
# API VIEWSET'İ
# =======================================================

class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
