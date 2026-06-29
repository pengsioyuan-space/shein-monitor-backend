from django.core.management.base import BaseCommand
from orders.models import Order
from miaoshou_v63 import fetch_orders


class Command(BaseCommand):
    help = "同步妙手订单"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        data = fetch_orders()

        # ⭐ 防止 None 崩溃
        if not data:
            print("❌ 没有获取到数据（data=None/空）")
            return

        if not isinstance(data, list):
            print("❌ 数据格式异常：", type(data))
            print(data)
            return

        new_count = 0
        update_count = 0

        for item in data:
            if not isinstance(item, dict):
                continue

            obj, created = Order.objects.get_or_create(
                order_no=item.get("order_no") or item.get("order_sn") or "",
                defaults={
                    "shop_name": item.get("shop_name", ""),
                    "region": item.get("region", ""),
                    "created_hours": item.get("created_hours", 0),
                    "logistics_no": item.get("logistics_no", ""),
                }
            )

            if created:
                new_count += 1
            else:
                update_count += 1

        print(f"✅ 同步完成：新增 {new_count} 条，更新 {update_count} 条")
