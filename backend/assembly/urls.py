from django.urls import path
from . import views

urlpatterns = [
    path('assembly/new/', views.create_aircraft_assembly, name='create_assembly'),
    
    # Bu URL, boş HTML sayfasını gösterir
    path('aircrafts/', views.list_aircrafts, name='list_aircrafts'),
    
    # Bu URL, DataTables'ın veri çekmek için kullanacağı API endpoint'idir
    path('api/aircrafts-datatable/', views.AircraftListJson.as_view(), name='api_aircrafts_datatable'),
]
