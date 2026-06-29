from django.http import JsonResponse, HttpResponse
from .models import Order
import csv


def orders_list(request):
    qs = Order.objects.all()

    return JsonResponse({
        "total": qs.count(),
        "data": list(qs.values())
    })


def export_orders(request):
    qs = Order.objects.all()

    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(resp)
    writer.writerow(["订单号", "店铺", "区域", "时间", "物流号"])

    for o in qs:
        writer.writerow([o.order_no, o.shop_name, o.region, o.created_time, o.logistics_no])

    return resp
