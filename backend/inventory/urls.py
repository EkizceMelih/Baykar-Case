from django.urls import path
from . import views

urlpatterns = [
    # Mevcut URL'ler
    path('parts/', views.part_list, name='part-list'),
    path('parts/add/', views.add_part, name='add-part'),
    path('parts/<int:part_id>/recycle/', views.recycle_part, name='recycle-part'),

    # YENİ: DataTables API endpoint'i
    path('api/parts-datatable/', views.PartListJson.as_view(), name='api_parts_datatable'),
]
