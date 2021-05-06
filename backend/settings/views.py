from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .serializers import SettingsSerializer
from .models import Settings

class SettingsView(viewsets.ModelViewSet):
    serializer_class = SettingsSerializer
    queryset = Settings.objects.all()