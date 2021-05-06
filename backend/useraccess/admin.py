from django.contrib import admin
from .models import SchedulerUser

class SchedulerAdmin(admin.ModelAdmin):
    model = SchedulerUser
    list_display = ("email", "first_name", "last_name", "AccessLevel")

admin.site.register(SchedulerUser, SchedulerAdmin)