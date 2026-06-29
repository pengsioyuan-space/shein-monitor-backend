
from django.core.management.base import BaseCommand
from miaoshou_v63 import fetch_all_packages, read_key_file
from orders.models import Order
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        app_key, app_secret = read_key_file()
        packages = fetch_all_packages(app_key, app_secret)

        for p in packages:
            order_no = p.get('order_no') or p.get('platformOrderSn')
            if not order_no:
                continue

            Order.objects.update_or_create(
                order_no=order_no,
                defaults={
                    'shop_name': p.get('shop_name',''),
                    'region': p.get('region','OTHER'),
                    'created_hours': p.get('created_hours',0),
                    'logistics_no': p.get('logistics_no','')
                }
            )

        print('sync done')
