from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import reverse
from collections import defaultdict

# DataTables için kütüphane
from django_datatables_view.base_datatable_view import BaseDatatableView


from .models import Part
from .forms import PartForm
from users.models import Team
from assembly.models import Aircraft

# DRF için importlar
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import PartSerializer


@login_required
def part_list(request):
    user = request.user
    if not hasattr(user, 'team') or not user.team:
        return HttpResponseForbidden("Bir takıma ait olmalısınız!")

    if user.team.type == Team.TeamType.MONTAJ:
        part_counts = Part.objects.filter(status='AVAILABLE').values('aircraft_model', 'type').annotate(count=Count('id')).order_by('aircraft_model', 'type')
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
        return render(request, "inventory/assembly_dashboard.html", context)
    else:
        return render(request, "inventory/part_list.html")


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
    if user_team_type == Team.TeamType.MONTAJ or part.type != user_team_type:
        return HttpResponseForbidden("Bu parçayı geri dönüşüme gönderme yetkiniz yok.")
    if part.status == Part.Status.AVAILABLE:
        part.status = Part.Status.RECYCLED
        part.save()
    return redirect("part-list")


# DataTables için API View'ı
class PartListJson(BaseDatatableView):
    model = Part
    columns = ['serial_number', 'type', 'aircraft_model', 'status', 'created_by__username', 'actions']
    order_columns = ['serial_number', 'type', 'aircraft_model', 'status', 'created_by__username', '']

    def get_initial_queryset(self):
        user = self.request.user
        team_type = user.team.type
        return Part.objects.filter(type=team_type, status='AVAILABLE').select_related('created_by')

    def render_column(self, row, column):
        #  "created_by__username" kolonunu manuel olarak formatlıyoruz.
        if column == 'created_by__username':
            return row.created_by.username if row.created_by else 'Bilinmiyor'
        elif column == 'type':
            return row.get_type_display()
        elif column == 'aircraft_model':
            return row.get_aircraft_model_display()
        elif column == 'status':
            return row.get_status_display()
        elif column == 'actions':
            recycle_url = reverse('recycle-part', args=[row.id])
            return format_html(f'<a href="{recycle_url}" class="btn btn-danger btn-sm">Geri Dönüşüme Gönder</a>')
        else:
            return super().render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(serial_number__icontains=search) |
                Q(aircraft_model__icontains=search) |
                Q(created_by__username__icontains=search)
            )
        return qs


# API VIEWSET'İ
class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
