from django.urls import path, include

urlpatterns = [
    path("dashboard/", include("dashboard.urls")),
    path("orders/", include("orders.urls")),
]
