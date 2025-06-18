from django import forms
from .models import Part

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
       
        fields = ['type', 'aircraft_model']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'readonly': True}),
            'aircraft_model': forms.Select(attrs={'class': 'form-control'}),
        }