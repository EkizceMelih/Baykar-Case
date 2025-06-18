from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

# --- Swagger/OpenAPI ---
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# --- ViewSet'ler ---
from assembly.views import AircraftViewSet
from inventory.views import PartViewSet



# --- Swagger Schema ---
schema_view = get_schema_view(
    openapi.Info(
        title="AirProd API",
        default_version="v1",
        description="Uçak üretim yönetim sistemi API dokümantasyonu",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# --- DRF Router Tanımı ---
router = DefaultRouter()
router.register(r"parts", PartViewSet, basename="part")
router.register(r"aircrafts", AircraftViewSet, basename="aircraft")

urlpatterns = [
    # YÖNETİM & API URL'leriM
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include('users.api_urls')), # <-- API Auth URL'leri artık buradan yönetiliyor.
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # WEB SAYFASI URL'lerim
    path("accounts/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("inventory/", include('inventory.urls')),
    path("assembly/", include('assembly.urls')),
    path("", RedirectView.as_view(url="/accounts/login/", permanent=True), name="home"),
]