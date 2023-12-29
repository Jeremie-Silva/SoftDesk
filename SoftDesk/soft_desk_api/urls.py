from django.urls import path
from .views import running


urlpatterns = [
    path("", running, name="running")
]
