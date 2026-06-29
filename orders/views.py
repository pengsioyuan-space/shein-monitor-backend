from django.http import JsonResponse, HttpResponse
from .models import Order
import csv


# =========================
# 📦 1. 订单列表接口
# =========================
def orders_list(request):
    qs = Order.objects.all().order_by("-id")

    data = []
    for o in qs:
        data.append({
            "order_no": o.order_no,
            "shop_name": o.shop_name,
            "region": o.region,
            "created_hours": o.created_hours,
            "logistics_no": o.logistics_no,
        })

    return JsonResponse({"data": data})


# =========================
# 📥 2. 导出订单接口
# =========================
def export_orders(request):
    qs = Order.objects.all()

    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=orders.csv'

    writer = csv.writer(resp)
    writer.writerow(["订单号", "店铺", "区域", "时间", "物流号"])

    for o in qs:
        writer.writerow([
            o.order_no,
            o.shop_name,
            o.region,
            o.created_hours,
            o.logistics_no
        ])

    return resp
