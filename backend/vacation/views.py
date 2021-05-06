from django.shortcuts import render

from rest_framework import viewsets
from .serializers import RequestsSerializer
from .models import VacationRequests

class RequestsView(viewsets.ModelViewSet):
    serializer_class = RequestsSerializer
    queryset = VacationRequests.objects.all()
