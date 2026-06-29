from django.urls import path, include
from dashboard.views import dashboard

urlpatterns = [
    path("", dashboard),   # ⭐ 关键：根路径
    path("orders/", include("orders.urls")),
]
