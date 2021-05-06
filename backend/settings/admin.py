from django.contrib import admin
from .models import Settings

# added for this project
@admin.register(Settings)
class SettingsrAdmin(admin.ModelAdmin):  
    list_display = ("description", "StartSchedule", "EndSchedule")
