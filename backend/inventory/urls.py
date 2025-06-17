# backend/inventory/urls.py

from django.urls import path
from .views import part_list, add_part, recycle_part

# Bu dosya, inventory uygulamasına ait web sayfası (template-tabanlı) URL'lerini yönetir.
# API URL'leri projenin ana urls.py dosyasındaki router tarafından yönetilmektedir.

urlpatterns = [
    path('parts/', part_list, name='part-list'),
    path('parts/add/', add_part, name='add-part'),
    path('parts/<int:part_id>/recycle/', recycle_part, name='recycle-part'),
]