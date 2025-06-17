from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User, Team

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    team     = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())

    class Meta:
        model  = User
        fields = ('id', 'username', 'password', 'team')

    def create(self, validated_data):
        # ORM üzerinden DB’ye INSERT yapar
        user = User.objects.create_user(
            username = validated_data['username'],
            password = validated_data['password'],
            team     = validated_data['team']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token    = serializers.CharField(read_only=True)

    def validate(self, data):
        # authenticate() direkt olarak auth_user tablosuna bakar
        user = authenticate(
            username = data.get('username'),
            password = data.get('password')
        )
        if not user:
            raise serializers.ValidationError("Kullanıcı adı veya şifre hatalı.")
        token, _ = Token.objects.get_or_create(user=user)
        return {
            'username': user.username,
            'token':    token.key
        }
