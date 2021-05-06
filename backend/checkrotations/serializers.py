from rest_framework import serializers 
from .models import RotationStatus

class RotationStatusSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = RotationStatus 
        fields = ['id', 'Status']