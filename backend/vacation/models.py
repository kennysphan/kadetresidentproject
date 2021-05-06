from django.db import models

class VacationRequests(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    requestOne = models.DateField(null=True, blank=True)
    requestTwo = models.DateField(null=True, blank=True)
    requestThree = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.email