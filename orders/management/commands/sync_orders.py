from django.core.management.base import BaseCommand
from orders.models import Order
from miaoshou_v63 import fetch_orders


class Command(BaseCommand):
    help = "同步妙手订单（稳定版）"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        try:
            data = fetch_orders()
        except Exception as e:
            print("❌ fetch_orders崩溃:", e)
            return

        if not data:
            print("⚠️ 没有数据")
            return

        if not isinstance(data, list):
            print("❌ 数据格式错误:", type(data))
            return

        new_count = 0
        skip_count = 0

        for item in data:
            if not isinstance(item, dict):
                continue

            order_no = item.get("order_no") or item.get("orderSn")

            if not order_no:
                skip_count += 1
                continue

            obj, created = Order.objects.get_or_create(
                order_no=order_no,
                defaults={
                    "shop_name": item.get("shop_name", ""),
                    "region": item.get("region", ""),
                    "created_hours": item.get("created_hours", 0),
                    "logistics_no": item.get("logistics_no", ""),
                }
            )

            if created:
                new_count += 1

        print(f"✅ 完成：新增 {new_count} 条，跳过 {skip_count} 条")
