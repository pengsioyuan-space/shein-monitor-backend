from django.core.management.base import BaseCommand
from orders.models import Order
from orders.miaoshou_v63 import fetch_orders  # 👈 关键：你的真实脚本


class Command(BaseCommand):
    help = "同步订单数据"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        data = fetch_orders()  # 👈 从你真实脚本拿数据

        new_count = 0
        skip_count = 0

        for item in data:
            obj, created = Order.objects.get_or_create(
                order_no=item["order_no"],
                defaults={
                    "shop_name": item.get("shop_name", ""),
                    "region": item.get("region", "OTHER"),
                    "created_hours": item.get("created_hours", 0),
                    "logistics_no": item.get("logistics_no", ""),
                }
            )

            if created:
                new_count += 1
            else:
                skip_count += 1

        print(f"✅ 同步完成：新增 {new_count} 条，跳过 {skip_count} 条")
