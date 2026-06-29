from django.http import JsonResponse, HttpResponse
from orders.models import Order
import csv


# =====================
# 📊 dashboard
# =====================
def dashboard(request):
    qs = Order.objects.all()

    data = {
        "total": qs.count(),
        "eu": qs.filter(region="EU").count(),
        "us": qs.filter(region="US").count(),
        "ca": qs.filter(region="CA").count(),
        "t12": qs.filter(created_hours__gte=12).count(),
        "t24": qs.filter(created_hours__gte=24).count(),
        "t36": qs.filter(created_hours__gte=36).count(),
        "t48": qs.filter(created_hours__gte=48).count(),
    }

    return JsonResponse({
        "code": 0,
        "data": data
    })


# =====================
# 📦 order list（前端用这个）
# =====================
def order_list(request):
    qs = Order.objects.all().order_by("-id")[:200]

    data = []
    for o in qs:
        data.append({
            "order_no": o.order_no,
            "shop_name": o.shop_name,
            "region": o.region,
            "created_hours": o.created_hours,
            "logistics_no": o.logistics_no,
        })

    return JsonResponse({
        "code": 0,
        "data": data
    })


# =====================
# 📥 export CSV
# =====================
def export_ops_orders(request):
    qs = Order.objects.all()

    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="ops_orders.csv"'

    w = csv.writer(resp)
    w.writerow(["订单号", "店铺", "区域", "小时", "物流号"])

    for o in qs:
        w.writerow([o.order_no, o.shop_name, o.region, o.created_hours, o.logistics_no])

    return resp
