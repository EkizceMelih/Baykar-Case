from django.urls import path
from .views import (
    RegisterAPI,
    LoginAPI,
    CustomAuthToken,
    ProfileAPI,
)

# Bu urlpatterns listesi, /api/auth/ ön eki ile gelen istekleri karşılayacak.
urlpatterns = [
    # /api/auth/register/
    path("register/", RegisterAPI.as_view(), name="api_register"),
    # /api/auth/login/
    path("login/", LoginAPI.as_view(), name="api_login"),
    # /api/auth/token/
    path("token/", CustomAuthToken.as_view(), name="api_token_auth"),
    # /api/auth/profile/
    path("profile/", ProfileAPI.as_view(), name="api_profile"),
]