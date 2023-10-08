from django.contrib import admin
from .models import Location

@admin.register(Location)
class GeoAdmin(admin.ModelAdmin):
    search_fields = ['address',]
