from django.db import models

class Criteria(models.Model):
    YEAR_CHOICES = (
        ('NA', 'not applicable'),
        ('1', 'PGY1'),
        ('2', 'PGY2'),
        ('3', 'PGY3'),
        ('4', 'PGY4'),
        ('5', 'PGY5'),
    )
    RotationType = models.CharField(max_length=120)
    StartRotation = models.DateField(null=True, blank=True)
    EndRotation = models.DateField(null=True, blank=True)
    MinResident = models.PositiveIntegerField()
    MaxResident = models.PositiveIntegerField()
    MinContinuedWeeks = models.PositiveIntegerField()
    MaxContinuedWeeks = models.PositiveIntegerField()
    Overnight = models.BooleanField(default=False)
    Essential = models.BooleanField(default=False)
    ResidentYear = models.CharField(
        max_length=20,
        choices=YEAR_CHOICES,
        default=None,
    )

    def __str__(self):
        return self.RotationType