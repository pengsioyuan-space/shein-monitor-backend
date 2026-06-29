from django.urls import path
from .views import dashboard_data

urlpatterns = [
    path("api/dashboard/", dashboard_data),
]
