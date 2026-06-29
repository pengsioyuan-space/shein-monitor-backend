from django.urls import path
from .views import orders_list, export_orders

urlpatterns = [
    path("list/", orders_list),
    path("export/", export_orders),
]
