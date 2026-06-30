from django.core.management.base import BaseCommand
from orders.models import Order

import os
import sys

# sync_orders.py 在 /app/orders/management/commands/ 下；项目根目录是 /app
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from miaoshou_v63 import fetch_orders


REGION_RULES = {
    "EU": [
        "EU", "EUR", "EURO", "EUROPE", "欧盟", "欧洲",
        "DE", "FR", "ES", "IT", "NL", "PL", "SE", "BE", "AT", "IE", "PT",
        "GERMANY", "FRANCE", "SPAIN", "ITALY", "NETHERLANDS", "POLAND",
    ],
    "US": [
        "US", "USA", "UNITED STATES", "AMERICA", "美国", "美区", "北美",
    ],
    "CA": [
        "CA", "CANADA", "加拿大", "加区",
    ],
}


def safe_str(value):
    if value is None:
        return ""
    return str(value).strip()


def to_float(value, default=0):
    try:
        if value in [None, ""]:
            return default
        return float(value)
    except Exception:
        return default


def infer_region(*values):
    """
    根据店铺名/订单号等文本自动识别 EU / US / CA。
    没命中返回 OTHER，避免前端统计为空。
    """
    text = " ".join(safe_str(v) for v in values if safe_str(v)).upper()
    if not text:
        return "OTHER"

    for region, keywords in REGION_RULES.items():
        for keyword in keywords:
            kw = keyword.upper()
            if kw and kw in text:
                return region
    return "OTHER"


def model_has_field(name):
    try:
        Order._meta.get_field(name)
        return True
    except Exception:
        return False


class Command(BaseCommand):
    help = "同步妙手订单（v6.3）：自动地区识别 + update_or_create 去重"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        try:
            rows = fetch_orders()
        except Exception as e:
            print("❌ fetch_orders 执行失败：", e)
            return

        if rows is None:
            print("❌ 返回 None")
            return

        if not isinstance(rows, list):
            print("❌ 数据类型错误：", type(rows))
            return

        print(f"📦 拉取到订单数：{len(rows)}")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in rows:
            if not isinstance(item, dict):
                skipped_count += 1
                continue

            order_no = safe_str(
                item.get("订单编号")
                or item.get("order_no")
                or item.get("orderSn")
                or item.get("platformOrderSn")
            )

            if not order_no:
                skipped_count += 1
                continue

            shop_name = safe_str(item.get("店铺") or item.get("shop_name"))
            created_hours = to_float(item.get("已创建小时数") or item.get("created_hours"), 0)
            logistics_no = safe_str(item.get("物流单号") or item.get("logistics_no"))
            created_time = safe_str(item.get("订单创建时间") or item.get("created_time"))
            package_no = safe_str(item.get("妙手包裹号") or item.get("package_no"))
            fulfillment_type = safe_str(item.get("履约类型") or item.get("fulfillment_type"))
            region = safe_str(item.get("region")) or infer_region(shop_name, order_no)

            defaults = {}
            if model_has_field("shop_name"):
                defaults["shop_name"] = shop_name
            if model_has_field("region"):
                defaults["region"] = region
            if model_has_field("created_hours"):
                defaults["created_hours"] = created_hours
            if model_has_field("logistics_no"):
                defaults["logistics_no"] = logistics_no
            if model_has_field("created_time"):
                defaults["created_time"] = created_time
            if model_has_field("package_no"):
                defaults["package_no"] = package_no
            if model_has_field("fulfillment_type"):
                defaults["fulfillment_type"] = fulfillment_type

            obj, created = Order.objects.update_or_create(
                order_no=order_no,
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        print(
            f"✅ 同步完成：新增 {created_count} 条 / 更新 {updated_count} 条 / 跳过 {skipped_count} 条"
        )
