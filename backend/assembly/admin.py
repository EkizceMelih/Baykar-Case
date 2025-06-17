from django.contrib import admin
from .models import Aircraft, AircraftPart

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'created_by', 'created_at')
    list_filter  = ('type', 'created_by')

@admin.register(AircraftPart)
class AircraftPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'part', 'aircraft')
