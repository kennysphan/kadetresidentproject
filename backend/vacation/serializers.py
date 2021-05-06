from rest_framework import serializers 
from .models import VacationRequests

class RequestsSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = VacationRequests 
        fields = ['id', 'email', 'requestOne', 'requestTwo', 'requestThree']