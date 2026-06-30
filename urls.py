from django.contrib import admin
from django.urls import path, include
from orders import views as order_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", order_views.dashboard),
    path("dashboard/", order_views.dashboard),
    path("orders/", include("orders.urls")),
]
