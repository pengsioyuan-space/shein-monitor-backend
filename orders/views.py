
import csv
from django.http import HttpResponse
from orders.models import Order

def export_ops_orders(request):
    qs = Order.objects.filter(created_hours__gte=12)

    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=ops.csv'

    w = csv.writer(resp)
    w.writerow(['订单号','店铺','区域','小时','物流单号'])

    for o in qs:
        w.writerow([o.order_no,o.shop_name,o.region,o.created_hours,o.logistics_no])

    return resp
