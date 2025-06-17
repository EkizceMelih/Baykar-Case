# backend/aircraft_production/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from users.views import ProfileView

# Swagger/OpenAPI
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# ViewSet’ler
from inventory.views import PartViewSet
from assembly.views import AircraftViewSet

# Auth API’leri
from users.views import (
    RegisterAPI,
    LoginAPI,
    CustomAuthToken,
    ProfileAPI,
    RegisterView,      # ← form-tabanlı kayıt sayfası için
)

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
router.register(r"parts",     PartViewSet,     basename="part")
router.register(r"aircrafts", AircraftViewSet, basename="aircraft")

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),

    # API: JSON register & login
    path("api/auth/register/", RegisterAPI.as_view(),    name="api_register"),
    path("api/auth/login/",    LoginAPI.as_view(),       name="api_login"),

    # API: Token-bazlı login & profile
    path("api/auth/token/",    CustomAuthToken.as_view(), name="api_token"),
    path("api/auth/profile/",  ProfileAPI.as_view(),     name="api_profile"),

    # DRF Token Auth (alternatif; CustomAuthToken kullanıyorsan kaldırabilirsin)
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),

    # DRF browsable API login/logout
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),

    # CRUD uç noktaları
    path("api/", include(router.urls)),

    # Swagger/OpenAPI uç noktaları
    path("swagger(.json|.yaml)", schema_view.without_ui(cache_timeout=0),  name="schema-json"),
    path("swagger/",              schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/",                schema_view.with_ui("redoc", cache_timeout=0),   name="schema-redoc"),

    # Form-tabanlı auth: kayıt, login, logout, password-işlemleri
    path("accounts/register/", RegisterView.as_view(), name="register"),  # ← eklenen kayıt rotası
    path("accounts/", include("django.contrib.auth.urls")),


    path("accounts/profile/", ProfileView.as_view(), name="profile"),

]
