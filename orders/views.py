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
def order_list(request):
    if request.method == "OPTIONS":
        return add_cors(HttpResponse(""))

    qs = base_queryset(request)

    # 默认显示最新更新的订单
    if has_model_field("updated_at"):
        qs = qs.order_by("-updated_at", "-id")
    elif has_model_field("created_at"):
        qs = qs.order_by("-created_at", "-id")
    elif has_model_field("created_hours"):
        qs = qs.order_by("created_hours")
    else:
        qs = qs.order_by("-id")

    limit = request.GET.get("limit", "100")
    try:
        limit = int(limit)
    except Exception:
        limit = 100

    limit = max(1, min(limit, 500))

    data = []

    for o in qs[:limit]:
        data.append({
            "order_no": getattr(o, "order_no", ""),
            "shop_name": getattr(o, "shop_name", ""),
            "region": getattr(o, "region", ""),
            "created_hours": getattr(o, "created_hours", ""),
            "logistics_no": getattr(o, "logistics_no", ""),
            "updated_at": str(getattr(o, "updated_at", "")),
        })

    return add_cors(JsonResponse({"data": data}, json_dumps_params={"ensure_ascii": False}))

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
