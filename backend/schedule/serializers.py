from rest_framework import serializers 
from .models import Schedule
from .models import RotationsByWeek

class ScheduleSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Schedule 
        fields = ['id', 'email', 'name', 'postGradLevel', 'generatedSchedule', 'blackoutRotations', 'assignedRotations']

class RotationsByWeekSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = RotationsByWeek 
        fields = ['id', 'rotationWeek', 'availableRotations']