from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from orders.models import DashboardStats, Order


# =========================
# ① Dashboard 接口（前端首页）
# =========================
def dashboard(request):

    stat = DashboardStats.objects.order_by("-updated_at").first()

    # ❌ 没有缓存数据时 fallback（避免前端空白）
    if not stat:

        qs = Order.objects.all()

        data = {
            "total": qs.count(),
            "eu": qs.filter(region="EU").count(),
            "us": qs.filter(region="US").count(),
            "ca": qs.filter(region="CA").count(),
            "other": qs.exclude(region__in=["EU", "US", "CA"]).count(),

            "pending_process_risk": qs.filter(created_hours__gte=12).count(),
            "pending_ship_risk": qs.filter(created_hours__gte=24).count(),
            "pickup_appointment_risk": qs.filter(created_hours__gte=36).count(),
            "pickup_risk": qs.filter(created_hours__gte=48).count(),

            "risk_chart": {
                "即将处理超时": qs.filter(created_hours__gte=12).count(),
                "即将发货超时": qs.filter(created_hours__gte=24).count(),
                "即将预约取件超时": qs.filter(created_hours__gte=36).count(),
                "即将揽收超时": qs.filter(created_hours__gte=48).count(),
            },

            "region_chart": {
                "EU": qs.filter(region="EU").count(),
                "US": qs.filter(region="US").count(),
                "CA": qs.filter(region="CA").count(),
                "OTHER": qs.exclude(region__in=["EU", "US", "CA"]).count(),
            }
        }

        return JsonResponse(data)

    # ✅ 有缓存直接返回
    return JsonResponse(stat.data)


# =========================
# ② 订单列表接口（表格）
# =========================
def orders_list(request):

    qs = Order.objects.all()

    # 时间过滤（兼容你前端 start/end）
    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        qs = qs.filter(created_at__gte=parse_datetime(start))

    if end:
        qs = qs.filter(created_at__lte=parse_datetime(end))

    limit = int(request.GET.get("limit", 100))
    qs = qs.order_by("-created_at")[:limit]

    data = [
        {
            "order_no": o.order_no,
            "shop_name": o.shop_name,
            "region": o.region,
            "created_hours": o.created_hours,
            "logistics_no": o.logistics_no,
        }
        for o in qs
    ]

    return JsonResponse({
        "data": data
    })


# =========================
# ③ 导出接口（下载按钮）
# =========================
def orders_export(request):

    qs = Order.objects.all()

    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        qs = qs.filter(created_at__gte=parse_datetime(start))

    if end:
        qs = qs.filter(created_at__lte=parse_datetime(end))

    rows = [
        "订单号,店铺,区域,创建小时,物流号"
    ]

    for o in qs:
        rows.append(
            f"{o.order_no},{o.shop_name},{o.region},{o.created_hours},{o.logistics_no}"
        )

    content = "\n".join(rows)

    return JsonResponse({
        "content": content
    })
