from django.db import models

class VacationRequests(models.Model):
    PGY_CHOICES = (
        ('1', 'PGY1'),
        ('2', 'PGY2'),
        ('3', 'PGY3'),
        ('4', 'PGY4'),
        ('5', 'PGY5'),
    )

    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=254, default='')
    last_name = models.CharField(max_length=254, default='')
    requestOne = models.DateField(null=True, blank=True)
    requestTwo = models.DateField(null=True, blank=True)
    requestThree = models.DateField(null=True, blank=True)

    postGradLevel = models.CharField(
        max_length=4,
        choices=PGY_CHOICES,
        default=''
    )

    def __str__(self):
        return self.email