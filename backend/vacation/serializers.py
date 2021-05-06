from rest_framework import serializers 
from .models import VacationRequests

class RequestsSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = VacationRequests 
        fields = ['id', 'email', 'first_name', 'last_name', 'postGradLevel', 'requestOne', 'requestTwo', 'requestThree']