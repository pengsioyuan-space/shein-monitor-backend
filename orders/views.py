from django.http import JsonResponse
from .models import Order

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
