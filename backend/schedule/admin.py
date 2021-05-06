from django.contrib import admin
from .models import Schedule
from .models import RotationsByWeek

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):  
    list_display = ("email", "name", "postGradLevel", "generatedSchedule", "blackoutRotations", "assignedRotations")


@admin.register(RotationsByWeek)
class RotationsByWeekAdmin(admin.ModelAdmin):  
    list_display = ("rotationWeek", "availableRotations")