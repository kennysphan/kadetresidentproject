from django.urls import include, path
from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'api/grid', views.ScheduleView, 'schedule')
router.register(r'api/drop_down', views.RotationsByWeekView, 'rotationsByWeek')

urlpatterns = [
    path('', include(router.urls)),

]