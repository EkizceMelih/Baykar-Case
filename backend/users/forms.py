from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Team

class CustomUserCreationForm(UserCreationForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        label="Takım",
        empty_label="Takım seçin"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "team", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'team':     forms.Select(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
