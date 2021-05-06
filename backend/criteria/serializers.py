from rest_framework import serializers 
from .models import Criteria

class CriteriaSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Criteria 
        fields = ['id', 'RotationType', 'StartRotation', 'EndRotation', 'MinResident', 'MaxResident', 'MinContinuedWeeks', 'MaxContinuedWeeks', 'ResidentYear', 'Essential', 'Overnight']