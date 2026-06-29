from django.core.management.base import BaseCommand
from orders.models import Order
import traceback


class Command(BaseCommand):
    help = "同步订单（稳定版，不会因为单条数据崩溃）"

    def handle(self, *args, **options):
        self.stdout.write("🚀 开始同步订单...")

        try:
            # 👇 TODO: 这里替换成你真实抓取逻辑
            orders_data = self.fetch_orders()

            success_count = 0
            skip_count = 0

            for item in orders_data:
                try:
                    order_no = item.get("order_no")

                    # ⭐ 核心修复：不会报错版本
                    order, created = Order.objects.get_or_create(
                        order_no=order_no,
                        defaults={
                            "shop_name": item.get("shop_name", ""),
                            "region": item.get("region", "OTHER"),
                            "created_hours": item.get("created_hours"),
                            "logistics_no": item.get("logistics_no", ""),
                        }
                    )

                    if created:
                        success_count += 1
                    else:
                        # 已存在就更新（可选）
                        order.shop_name = item.get("shop_name", order.shop_name)
                        order.region = item.get("region", order.region)
                        order.save()

                except Exception as e:
                    skip_count += 1
                    print("❌ 单条订单处理失败：", e)
                    continue

            self.stdout.write(self.style.SUCCESS(
                f"✅ 同步完成：新增 {success_count} 条，跳过 {skip_count} 条"
            ))

        except Exception as e:
            print("❌ 同步任务整体失败：")
            traceback.print_exc()

    def fetch_orders(self):
        """
        👉 这里先给你 mock 数据
        后面你接 SHEIN / 你的接口
        """
        return [
            {
                "order_no": "A001",
                "shop_name": "Test Shop",
                "region": "EU",
                "created_hours": 10,
                "logistics_no": "L001"
            },
            {
                "order_no": "A002",
                "shop_name": "Test Shop2",
                "region": "US",
                "created_hours": 20,
                "logistics_no": "L002"
            }
        ]
