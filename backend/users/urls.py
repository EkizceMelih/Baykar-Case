from django.urls import path
from .views import RegisterView, ProfileView

# Bu urlpatterns listesi, /accounts/ ön eki ile gelen istekleri karşılayacak.
urlpatterns = [
    # /accounts/register/ URL'ini RegisterView'a yönlendirir.
    path('register/', RegisterView.as_view(), name='register'),
    
    # /accounts/profile/ URL'ini ProfileView'a yönlendirir.
    path('profile/', ProfileView.as_view(), name='profile'),
]