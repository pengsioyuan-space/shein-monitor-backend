
from django.urls import path
from dashboard.views import dashboard
from orders.views import export_ops_orders

urlpatterns = [
    path('', dashboard),
    path('export/', export_ops_orders),
]
