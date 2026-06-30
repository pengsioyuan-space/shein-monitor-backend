import csv
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from orders.models import Order


def has_model_field(name):
    return any(field.name == name for field in Order._meta.fields)


def add_cors(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def parse_time(text):
    if not text:
        return None

    text = str(text).strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            pass

    return None


def base_queryset(request):
    qs = Order.objects.all()

    start = request.GET.get("start")
    end = request.GET.get("end")

    start_dt = parse_time(start)
    end_dt = parse_time(end)

    if has_model_field("created_time"):
        field_name = "created_time"
    elif has_model_field("order_created_time"):
        field_name = "order_created_time"
    else:
        field_name = None

    if field_name and start_dt:
        qs = qs.filter(**{f"{field_name}__gte": start_dt})

    if field_name and end_dt:
        qs = qs.filter(**{f"{field_name}__lte": end_dt})

    return qs


def get_region_count(qs, region):
    if not has_model_field("region"):
        return 0
    return qs.filter(region=region).count()


def not_collected_filter():
    """
    现在先兼容数据库。
    如果以后你加 first_collected_time / is_collected 字段，这里会自动启用。
    """
    if has_model_field("first_collected_time"):
        return Q(first_collected_time__isnull=True) | Q(first_collected_time="")
    if has_model_field("is_collected"):
        return Q(is_collected=False)
    return Q()


def dashboard(request):

    stat = DashboardStats.objects.order_by("-updated_at").first()

    if not stat:
        return JsonResponse({"error": "no data"})

    return JsonResponse(stat.data)


def order_list(request):
    if request.method == "OPTIONS":
        return add_cors(HttpResponse(""))

    qs = base_queryset(request)

    if has_model_field("created_hours"):
        qs = qs.order_by("-created_hours")
    else:
        qs = qs.order_by("order_no")

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
        })

    return add_cors(JsonResponse({"data": data}, json_dumps_params={"ensure_ascii": False}))


def trend(request):
    if request.method == "OPTIONS":
        return add_cors(HttpResponse(""))

    qs = base_queryset(request)

    if has_model_field("created_hours"):
        risk_12 = qs.filter(created_hours__gte=12).count()
        risk_24 = qs.filter(created_hours__gte=24).count()
        risk_36 = qs.filter(created_hours__gte=36).count()
        risk_48 = qs.filter(created_hours__gte=48).count()
    else:
        risk_12 = risk_24 = risk_36 = risk_48 = 0

    data = {
        "labels": ["12h+", "24h+", "36h+", "48h+"],
        "values": [risk_12, risk_24, risk_36, risk_48],
    }

    return add_cors(JsonResponse(data, json_dumps_params={"ensure_ascii": False}))


def export_ops_orders(request):
    qs = base_queryset(request)

    if has_model_field("created_hours"):
        qs = qs.order_by("-created_hours")

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="ops_orders.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["订单号", "店铺", "区域", "已创建小时数", "物流号"])

    for o in qs:
        writer.writerow([
            getattr(o, "order_no", ""),
            getattr(o, "shop_name", ""),
            getattr(o, "region", ""),
            getattr(o, "created_hours", ""),
            getattr(o, "logistics_no", ""),
        ])

    return add_cors(response)
