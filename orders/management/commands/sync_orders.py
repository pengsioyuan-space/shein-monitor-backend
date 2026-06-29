from miaoshou_v63 import fetch_orders
from orders.models import Order
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "同步订单"

    def handle(self, *args, **kwargs):
        data = fetch_orders()

        print("开始同步订单...")

        new_count = 0

        for item in data:
            obj, created = Order.objects.get_or_create(
                order_no=item["订单编号"],
                defaults={
                    "shop_name": item["店铺"],
                    "region": "",   # 你后面可以补
                    "created_hours": item["已创建小时数"],
                    "logistics_no": item["物流单号"],
                }
            )

            if created:
                new_count += 1

        print(f"同步完成：新增 {new_count} 条")
