from django.core.management.base import BaseCommand
from orders.models import Order

import os
import sys


# /app/orders/management/commands/sync_orders.py -> /app
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from miaoshou_v63 import fetch_orders


class Command(BaseCommand):
    help = "同步妙手订单（v6.3）"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        try:
            data = fetch_orders()
        except Exception as e:
            print("❌ fetch_orders 执行失败：", e)
            return

        if data is None:
            print("❌ 返回 None")
            return

        if not isinstance(data, list):
            print("❌ 数据类型错误：", type(data))
            return

        print(f"📦 拉取到订单数：{len(data)}")

        new_count = 0
        update_count = 0
        skip_count = 0

        for item in data:
            if not isinstance(item, dict):
                skip_count += 1
                continue

            order_no = (
                item.get("订单编号")
                or item.get("order_no")
                or item.get("orderSn")
                or item.get("platformOrderSn")
            )

            order_no = str(order_no).strip() if order_no is not None else ""

            if not order_no:
                skip_count += 1
                continue

            defaults = {
                "shop_name": item.get("店铺") or item.get("shop_name", ""),
                "region": item.get("region", ""),
                "created_hours": item.get("已创建小时数") or item.get("created_hours", 0),
                "logistics_no": item.get("物流单号") or item.get("logistics_no", ""),
            }

            obj, created = Order.objects.get_or_create(
                order_no=order_no,
                defaults=defaults
            )

            if created:
                new_count += 1
            else:
                changed = False

                for field, value in defaults.items():
                    if getattr(obj, field, None) != value:
                        setattr(obj, field, value)
                        changed = True

                if changed:
                    obj.save(update_fields=list(defaults.keys()))
                    update_count += 1
                else:
                    skip_count += 1

        print(f"✅ 同步完成：新增 {new_count} 条 / 更新 {update_count} 条 / 跳过 {skip_count} 条")
