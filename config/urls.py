from django.urls import path, include
from dashboard.views import dashboard

urlpatterns = [
    path("", dashboard),
    path("dashboard/", dashboard),
    path("orders/", include("orders.urls")),
]
