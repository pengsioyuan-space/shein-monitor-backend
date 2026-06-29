from django.core.management.base import BaseCommand
from orders.models import Order
from datetime import datetime


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        print("🚀 开始同步订单...")

        data = self.mock_data()

        for item in data:
            Order.objects.update_or_create(
                order_no=item["order_no"],
                defaults={
                    "shop_name": item["shop_name"],
                    "region": item["region"],
                    "created_time": item["created_time"],
                    "logistics_no": item["logistics_no"],
                }
            )

        print("✅ 同步完成")


    def mock_data(self):
        return [
            {
                "order_no": "A10001",
                "shop_name": "Shop A",
                "region": "EU",
                "created_time": datetime.now(),
                "logistics_no": "L001"
            },
            {
                "order_no": "A10002",
                "shop_name": "Shop B",
                "region": "US",
                "created_time": datetime.now(),
                "logistics_no": "L002"
            }
        ]
