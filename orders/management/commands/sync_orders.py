from django.core.management.base import BaseCommand
from orders.models import Order
from miaoshou_v63 import main as fetch_orders


class Command(BaseCommand):
    help = "同步订单（稳定版）"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 开始同步订单...")

        data = fetch_orders()

        if not data:
            self.stdout.write("⚠️ 没有数据返回，跳过")
            return

        new_count = 0

        for item in data:
            if not item:
                continue

            obj, created = Order.objects.get_or_create(
                order_no=item.get("order_no"),
                defaults={
                    "shop_name": item.get("shop_name", ""),
                    "region": item.get("region", ""),
                    "created_hours": item.get("created_hours", 0),
                    "logistics_no": item.get("logistics_no", "")
                }
            )

            if created:
                new_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ 同步完成：新增 {new_count} 条")
        )
