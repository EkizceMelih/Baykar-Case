from django.urls import path
from . import views  # assembly klasöründeki views.py dosyasını import eder

# Bu urlpatterns listesi, assembly uygulamasına özel URL'leri tanımlar.
urlpatterns = [
    # 1. Yeni Uçak Montaj Sayfası
    # URL: /assembly/new/
    # View: views.create_aircraft_assembly
    # URL Adı (template'lerde kullanmak için): 'create_assembly'
    path('assembly/new/', views.create_aircraft_assembly, name='create_assembly'),

    # 2. Monte Edilmiş Uçakları Listeleme Sayfası
    # URL: /aircrafts/
    # View: views.list_aircrafts
    # URL Adı: 'list_aircrafts'
    path('aircrafts/', views.list_aircrafts, name='list_aircrafts'),

    # Not: Projenin ana sayfasına bir yönlendirme de ekleyebiliriz.
    # Örneğin, ana sayfa doğrudan monte edilmiş uçakları listelesin:
    # path('', views.list_aircrafts, name='home'),
]