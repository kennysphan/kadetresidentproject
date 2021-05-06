from django.db import models
from django.contrib.auth.models import AbstractUser

class SchedulerUser(AbstractUser):
    ACCESS_CHOICES = (
        ('NA', 'not applicable'),
        ('1', 'PGY1'),
        ('2', 'PGY2'),
        ('3', 'PGY3'),
        ('4', 'PGY4'),
        ('5', 'PGY5'),
    )
    AccessLevel = models.CharField(
        max_length=2,
        choices=ACCESS_CHOICES,
    )
    email = models.EmailField(max_length=254, unique=True, primary_key=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email