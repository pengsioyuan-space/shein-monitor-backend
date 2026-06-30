from django.http import JsonResponse, HttpResponse
from django.utils.dateparse import parse_datetime

from orders.models import DashboardStats, Order


# =========================
# Dashboard
# =========================
def dashboard(request):
    stat = DashboardStats.objects.order_by("-updated_at").first()

    # ❗ fallback（只在没有缓存时用）
    if not stat:
        qs = Order.objects.all()

        eu = qs.filter(region="EU").count()
        us = qs.filter(region="US").count()
        ca = qs.filter(region="CA").count()
        total = qs.count()
        other = total - eu - us - ca

        pending_process = qs.filter(created_hours__gte=12).count()
        pending_ship = qs.filter(created_hours__gte=24).count()
        pickup_appointment = qs.filter(created_hours__gte=36).count()
        pickup = qs.filter(created_hours__gte=48).count()

        return JsonResponse({
            "total": total,
            "eu": eu,
            "us": us,
            "ca": ca,
            "other": other,

            "pending_process_risk": pending_process,
            "pending_ship_risk": pending_ship,
            "pickup_appointment_risk": pickup_appointment,
            "pickup_risk": pickup,

            "risk_chart": {
                "即将处理超时": pending_process,
                "即将发货超时": pending_ship,
                "即将预约取件超时": pickup_appointment,
                "即将揽收超时": pickup,
            },

            "region_chart": {
                "EU": eu,
                "US": us,
                "CA": ca,
                "OTHER": other,
            }
        })

    # 正常情况：读缓存
    return JsonResponse(stat.data)


# =========================
# order list
# =========================
def order_list(request):
    qs = Order.objects.all()

    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        qs = qs.filter(created_at__gte=parse_datetime(start))

    if end:
        qs = qs.filter(created_at__lte=parse_datetime(end))

    qs = qs.order_by("-id")

    limit = int(request.GET.get("limit", 100))
    limit = max(1, min(limit, 500))

    data = []

    for o in qs[:limit]:
        data.append({
            "order_no": o.order_no,
            "shop_name": o.shop_name,
            "region": o.region,
            "created_hours": o.created_hours,
            "logistics_no": o.logistics_no,
        })

    return JsonResponse({"data": data})


# =========================
# export
# =========================
def orders_export(request):
    qs = Order.objects.all()

    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        qs = qs.filter(created_at__gte=parse_datetime(start))

    if end:
        qs = qs.filter(created_at__lte=parse_datetime(end))

    rows = ["订单号,店铺,区域,创建小时,物流号"]

    for o in qs:
        rows.append(
            f"{o.order_no},{o.shop_name},{o.region},{o.created_hours},{o.logistics_no}"
        )

    return JsonResponse({
        "content": "\n".join(rows)
    })
