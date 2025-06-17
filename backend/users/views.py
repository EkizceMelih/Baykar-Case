# backend/users/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class RegisterAPI(generics.CreateAPIView):
    """
    POST /api/auth/register/
    {
      "username": "alice",
      "password": "S3cr3tPwd",
      "team": 2
    }
    """
    permission_classes = [AllowAny]
    serializer_class   = RegisterSerializer


class LoginAPI(generics.GenericAPIView):
    """
    POST /api/auth/login/
    {
      "username": "alice",
      "password": "S3cr3tPwd"
    }
    returns {"username":"alice","token":"abcdef..."}
    """
    permission_classes = [AllowAny]
    serializer_class   = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomAuthToken(ObtainAuthToken):
    """
    POST /api/auth/token/
    {
      "username": "alice",
      "password": "S3cr3tPwd"
    }
    returns {"token":"abcdef...","user_id":5,"username":"alice"}
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token':    token.key,
            'user_id':  user.pk,
            'username': user.username,
        })


class ProfileAPI(APIView):
    """
    GET /api/auth/profile/
    Authorization: Token <token>
    returns { "id":..., "username":..., "team":"..." }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'id':       u.id,
            'username': u.username,
            'team':     u.team.name,
        })
class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class    = CustomUserCreationForm
    success_url   = reverse_lazy("login")  # kayıt olduktan sonra login sayfasına yönlendirir

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"