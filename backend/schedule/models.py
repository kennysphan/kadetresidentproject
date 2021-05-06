from django.db import models

class RotationsByWeek(models.Model):
    rotationWeek = models.PositiveIntegerField()
    availableRotations = models.JSONField(blank=True, null=True, default=list)

class Schedule(models.Model):
    PGY_CHOICES = (
        ('1', 'PGY1'),
        ('2', 'PGY2'),
        ('3', 'PGY3'),
        ('4', 'PGY4'),
        ('5', 'PGY5'),
    )

    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254)
    postGradLevel = models.CharField(
        max_length=1,
        choices=PGY_CHOICES,
        default=None,
    )
    generatedSchedule = models.JSONField(blank=True, null=True, default=dict)

    blackoutRotations = models.JSONField(blank=True, null=True, default=dict)
    assignedRotations = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return self.email