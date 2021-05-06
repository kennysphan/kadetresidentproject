from django.contrib import admin
from .models import VacationRequests

@admin.register(VacationRequests)
class RequestsAdmin(admin.ModelAdmin):  
    list_display = ("email", "requestOne", "requestTwo", "requestThree")
