from django.core.management.base import BaseCommand
from orders.models import Order
from miaoshou_v63 import fetch_orders


class Command(BaseCommand):
    help = "同步订单（稳定版）"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        # ======================
        # ⭐ 安全调用
        # ======================
        try:
            data = fetch_orders()
        except Exception as e:
            print("❌ fetch_orders 崩溃：", e)
            return

        # ======================
        # ⭐ 防 None
        # ======================
        if not data:
            print("⚠️ 没有获取到订单数据")
            return

        if not isinstance(data, list):
            print("❌ 数据格式错误：", type(data))
            return

        new_count = 0
        update_count = 0

        # ======================
        # ⭐ 原逻辑不动
        # ======================
        for item in data:
            if not isinstance(item, dict):
                continue

            obj, created = Order.objects.get_or_create(
                order_no=item.get("order_no", ""),
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
