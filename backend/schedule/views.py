from django.shortcuts import render

from rest_framework import viewsets
from .serializers import ScheduleSerializer
from .serializers import RotationsByWeekSerializer
from .models import Schedule
from .models import RotationsByWeek

class ScheduleView(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()

class RotationsByWeekView(viewsets.ModelViewSet):
    serializer_class = RotationsByWeekSerializer
    queryset = RotationsByWeek.objects.all()