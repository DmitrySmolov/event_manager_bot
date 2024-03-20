from django.urls import include, path
from rest_framework import routers

from .views import EventViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
