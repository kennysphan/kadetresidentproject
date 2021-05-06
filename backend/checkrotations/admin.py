from django.contrib import admin
from .models import RotationStatus

@admin.register(RotationStatus)
class RotationStatusAdmin(admin.ModelAdmin):  
    list_display = ("Status",)
