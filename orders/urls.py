from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard),
    path("list/", views.order_list),
    path("trend/", views.trend),
    path("export/", views.export_ops_orders),
]
