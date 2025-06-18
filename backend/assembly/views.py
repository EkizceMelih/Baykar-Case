from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db import transaction, models
from django.contrib import messages
from django.utils.html import format_html
from collections import defaultdict

# DataTables için kütüphane ve Q nesnesi
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q

# Diğer uygulamalardan modelleri import ediyoruz
from inventory.models import Part
from users.models import Team
from .models import Aircraft

# DRF ve Serializer importları
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import AircraftSerializer


class ValidationError(Exception):
    pass

# ==================================
# WEB SAYFASI VIEW'LARI
# ==================================
@login_required
@transaction.atomic
def create_aircraft_assembly(request):
    user = request.user
    if not hasattr(user, 'team') or user.team.type != Team.TeamType.MONTAJ:
        return HttpResponseForbidden("Bu işlemi yapma yetkiniz yok. Sadece Montaj Takımı erişebilir.")

    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        part_ids = {
            'KANAT': request.POST.get('KANAT'), 'GOVDE': request.POST.get('GOVDE'),
            'KUYRUK': request.POST.get('KUYRUK'), 'AVIYONIK': request.POST.get('AVIYONIK'),
        }
        try:
            if not all(part_ids.values()):
                raise ValidationError("Lütfen her parça tipi için bir seçim yapın.")
            selected_parts = Part.objects.filter(id__in=part_ids.values())
            if selected_parts.count() != 4:
                raise ValidationError("Parça seçiminde bir tutarsızlık var.")
            for part in selected_parts:
                if part.status != Part.Status.AVAILABLE:
                    raise ValidationError(f"Seçtiğiniz parça ({part.serial_number}) artık mevcut değil.")
                if part.aircraft_model != model_name:
                    raise ValidationError(f"Parça ({part.serial_number}) {model_name} modeli için uygun değil.")
            new_aircraft = Aircraft.objects.create(model_name=model_name, assembled_by=user)
            selected_parts.update(used_in_aircraft=new_aircraft, status=Part.Status.USED)
            messages.success(request, f"{new_aircraft.serial_number} seri numaralı {model_name} başarıyla monte edildi!")
            return redirect('list_aircrafts')
        except ValidationError as e:
            messages.error(request, e)
            return redirect('create_assembly')
        except Exception as e:
            messages.error(request, f"Beklenmedik bir hata oluştu: {e}")
            return redirect('create_assembly')
    
    aircraft_models_with_status = []
    all_part_types = [choice[0] for choice in Part.PartType.choices]
    for model_key, model_label in Aircraft.AircraftModel.choices:
        is_ready, missing_parts = True, []
        for part_type in all_part_types:
            if not Part.objects.filter(status='AVAILABLE', aircraft_model=model_key, type=part_type).exists():
                is_ready = False
                missing_parts.append(Part.PartType(part_type).label)
        aircraft_models_with_status.append({'key': model_key, 'label': model_label, 'ready': is_ready, 'missing': ", ".join(missing_parts)})
    
    available_parts = Part.objects.filter(status=Part.Status.AVAILABLE).order_by('serial_number')
    grouped_parts_dict = defaultdict(list)
    for part in available_parts:
        grouped_parts_dict[part.type].append(part)
    
    part_groups_for_template = []
    for type_key, type_label in Part.PartType.choices:
        part_groups_for_template.append({'key': type_key, 'label': type_label, 'parts': grouped_parts_dict.get(type_key, [])})

    context = {'aircraft_models_with_status': aircraft_models_with_status, 'part_groups': part_groups_for_template}
    return render(request, 'assembly/create_assembly.html', context)


@login_required
def list_aircrafts(request):
    return render(request, 'assembly/list_aircrafts.html')


# ==================================
# DATATABLES İÇİN API VIEW'I 
# ==================================

class AircraftListJson(BaseDatatableView):
    model = Aircraft
    columns = ['serial_number', 'model_name', 'assembled_by__username', 'assembly_date', 'parts']
    order_columns = ['serial_number', 'model_name', 'assembled_by__username', 'assembly_date', '']

    def get_initial_queryset(self):
        return Aircraft.objects.select_related('assembled_by').prefetch_related('parts')

    def render_column(self, row, column):
        if column == 'assembled_by__username':
            return row.assembled_by.username if row.assembled_by else 'Bilinmiyor'
        elif column == 'model_name':
            return row.get_model_name_display()
        elif column == 'parts':
            parts_html = "<ul class='list-unstyled mb-0'>" + "".join(
                [f"<li>{part.serial_number} <small class='text-muted'>({part.get_type_display()})</small></li>" for part in row.parts.all()]
            ) + "</ul>"
            return format_html(parts_html)
        else:
            return super().render_column(row, column)

    def filter_queryset(self, qs):
        """
        DataTables'ın arama kutusuna girilen değere göre filtreleme yapar.
        Bu özel metod, ilişkili alanlarda (örn: User.username) arama yapmayı sağlar.
        """
        search = self.request.GET.get('search[value]', None)
        if search:
            # Arama sorgusunu oluşturuyoruz
            q_objects = Q(serial_number__icontains=search) | \
                        Q(model_name__icontains=search) | \
                        Q(assembled_by__username__icontains=search)
            
            qs = qs.filter(q_objects)
        return qs


# ==================================
# DRF İÇİN API VIEWSET'İ
# ==================================

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all().order_by('-assembly_date')
    serializer_class = AircraftSerializer
    permission_classes = [IsAuthenticated]
