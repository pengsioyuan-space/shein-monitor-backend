from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard),
    path("list/", views.orders_list),
    path("export/", views.orders_export),
]
