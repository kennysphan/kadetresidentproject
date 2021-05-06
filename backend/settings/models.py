from django.db import models

class Settings(models.Model):
    description = models.CharField(max_length=120)
    StartSchedule = models.DateField()
    EndSchedule = models.DateField()
    DatesSet = models.BooleanField(default=False)

    def __str__(self):
        return self.description