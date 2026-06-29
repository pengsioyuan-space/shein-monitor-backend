from django.core.management.base import BaseCommand
from orders.models import Order
from orders.miaoshou_v63 import main as fetch_orders


class Command(BaseCommand):
    help = "同步妙手订单"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单")

        data = fetch_orders()  # ⚠️ 这里要改成“返回数据版本”

        new_count = 0

        for item in data:
            obj, created = Order.objects.get_or_create(
                order_no=item["order_no"],
                defaults={
                    "shop_name": item.get("shop_name", ""),
                    "region": item.get("region", ""),
                    "created_hours": item.get("created_hours", 0),
                    "logistics_no": item.get("logistics_no", ""),
                }
            )

            if created:
                new_count += 1

        print(f"✅ 同步完成：新增 {new_count} 条")
