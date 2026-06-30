from django.core.management.base import BaseCommand
from orders.models import Order
import importlib


EU_KEYWORDS = [
    "EU", "欧盟", "欧洲", "德国", "法国", "意大利", "西班牙", "荷兰", "波兰",
    "DE", "FR", "IT", "ES", "NL", "PL"
]

US_KEYWORDS = [
    "US", "USA", "美国", "美区"
]

CA_KEYWORDS = [
    "CA", "CANADA", "加拿大"
]


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


def has_model_field(name):
    return any(field.name == name for field in Order._meta.fields)


def infer_region(shop_name="", order_no="", raw_region=""):
    text = f"{shop_name} {order_no} {raw_region}".upper()

    if raw_region:
        r = raw_region.upper()
        if r in ["EU", "US", "CA"]:
            return r

    for key in US_KEYWORDS:
        if key.upper() in text:
            return "US"

    for key in CA_KEYWORDS:
        if key.upper() in text:
            return "CA"

    for key in EU_KEYWORDS:
        if key.upper() in text:
            return "EU"

    return "OTHER"


def get_rows_from_miaoshou():
    """
    不要求 miaoshou_v63.py 必须有 fetch_orders。
    如果有 fetch_orders，就用 fetch_orders。
    如果没有，就直接复用原来的 read_key_file / fetch_all_packages / build_rows。
    这样不破坏你原 v6.3 逻辑。
    """
    miaoshou = importlib.import_module("miaoshou_v63")

    if hasattr(miaoshou, "fetch_orders"):
        rows = miaoshou.fetch_orders()
        return rows or []

    app_key, app_secret = miaoshou.read_key_file(miaoshou.KEY_FILE)
    packages = miaoshou.fetch_all_packages(app_key, app_secret)
    rows = miaoshou.build_rows(app_key, app_secret, packages)
    return rows or []


class Command(BaseCommand):
    help = "同步妙手近2天订单到数据库"

    def handle(self, *args, **kwargs):
        print("🚀 开始同步订单...")

        try:
            rows = get_rows_from_miaoshou()
        except Exception as e:
            print("❌ 妙手同步失败：", e)
            return

        if not rows:
            print("⚠️ 妙手没有返回订单")
            return

        print(f"📦 妙手返回订单数：{len(rows)}")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in rows:
            if not isinstance(item, dict):
                skipped_count += 1
                continue

            order_no = (
                safe_str(item.get("订单编号"))
                or safe_str(item.get("order_no"))
                or safe_str(item.get("orderSn"))
                or safe_str(item.get("platformOrderSn"))
            )

            if not order_no:
                skipped_count += 1
                continue

            shop_name = safe_str(item.get("店铺")) or safe_str(item.get("shop_name"))
            logistics_no = safe_str(item.get("物流单号")) or safe_str(item.get("logistics_no"))
            created_hours = to_float(item.get("已创建小时数") or item.get("created_hours"), 0)
            created_time = safe_str(item.get("订单创建时间")) or safe_str(item.get("created_time"))
            package_no = safe_str(item.get("妙手包裹号")) or safe_str(item.get("package_no"))
            fulfillment_type = safe_str(item.get("履约类型")) or safe_str(item.get("fulfillment_type"))

            region = infer_region(
                shop_name=shop_name,
                order_no=order_no,
                raw_region=safe_str(item.get("region")),
            )

            defaults = {}

            if has_model_field("shop_name"):
                defaults["shop_name"] = shop_name

            if has_model_field("region"):
                defaults["region"] = region

            if has_model_field("created_hours"):
                defaults["created_hours"] = created_hours

            if has_model_field("logistics_no"):
                defaults["logistics_no"] = logistics_no

            if has_model_field("created_time"):
                defaults["created_time"] = created_time

            if has_model_field("order_created_time"):
                defaults["order_created_time"] = created_time

            if has_model_field("package_no"):
                defaults["package_no"] = package_no

            if has_model_field("fulfillment_type"):
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
