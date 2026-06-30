from django.contrib import admin
from django.urls import path, include
from orders import views as order_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # 根路径直接返回 dashboard，方便你打开 Railway 域名就看到数据
    path("", order_views.dashboard),

    path("dashboard/", order_views.dashboard),
    path("orders/", include("orders.urls")),
]
