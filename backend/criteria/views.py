from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .serializers import CriteriaSerializer
from .models import Criteria

class CriteriaView(viewsets.ModelViewSet):
    serializer_class = CriteriaSerializer
    queryset = Criteria.objects.all()