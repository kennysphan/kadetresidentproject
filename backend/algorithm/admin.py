from django.contrib import admin
from .models import AlgorithmStatus

@admin.register(AlgorithmStatus)
class AlgorithmStatusAdmin(admin.ModelAdmin):  
    list_display = ("Status",)
