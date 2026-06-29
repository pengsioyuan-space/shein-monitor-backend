# -*- coding: utf-8 -*-

import os
import json
import time
import hmac
import hashlib
import requests
from datetime import datetime, timezone, timedelta

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta


# =========================
# 配置
# =========================

DOMAIN = "https://openapi-erp.91miaoshou.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(SCRIPT_DIR, "miaoshou_key.txt")

#本地时间近2天，即48h
def get_time_range(days=2):
    now = datetime.now()

    start = now - timedelta(days=days)
    end = now

    return (
        start.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )

PAGE_SIZE = 100
PAGE_START = 1
MAX_PAGES = 1000

CREATE_TZ = timezone(timedelta(hours=8))


# =========================
# 工具
# =========================

def safe(v):
    return "" if v is None else str(v)


def read_keys():
    data = {}
    with open(KEY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                data[k.lower()] = v.strip()

    return data["appkey"], data["appsecret"]


def sign(app_key, app_secret, path, ts, body):
    raw = f"{app_secret}{path}{ts}{app_key}{body}{app_secret}"
    return hmac.new(app_secret.encode(), raw.encode(), hashlib.sha256).hexdigest()


def request_api(app_key, app_secret, path, body):
    url = DOMAIN + path
    body_json = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    ts = str(int(time.time()))

    headers = {
        "x-app-key": app_key,
        "x-timestamp": ts,
        "x-sign": sign(app_key, app_secret, path, ts, body_json),
        "Content-Type": "application/json",
    }

    r = requests.post(url, data=body_json.encode(), headers=headers, timeout=30)
    return r.json()


# =========================
# 妙手拉取
# =========================

def fetch_packages():
    app_key, app_secret = read_keys()
    all_data = []

    ORDER_START_FROM, ORDER_START_TO = get_time_range(2)  # 👈 最近2天

    for page in range(PAGE_START, PAGE_START + MAX_PAGES):
        body = {
            "page": page,
            "pageSize": PAGE_SIZE,
            "gmtCreateFrom": ORDER_START_FROM,
            "gmtCreateTo": ORDER_START_TO
        }

        res = request_api(app_key, app_secret,
                          "/open/v1/order/package/fetch/search_package_list",
                          body)

        data = res.get("data", {})
        lst = data.get("list") or data.get("orderPackageList") or []

        if not lst:
            break

        all_data.extend(lst)

        if len(lst) < PAGE_SIZE:
            break

        time.sleep(0.1)

    return all_data


# =========================
# 数据整理（给 Django 用）
# =========================

def build_rows(packages):
    rows = []

    now = datetime.now(CREATE_TZ)

    for p in packages:

        create_time = p.get("gmtCreate") or ""
        try:
            dt = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=CREATE_TZ)
        except:
            dt = None

        hours = ""
        if dt:
            hours = round((now - dt).total_seconds() / 3600, 2)

        rows.append({
            "订单编号": p.get("orderNo") or "",
            "店铺": p.get("shopName") or "",
            "区域": p.get("region") or "",
            "时间": create_time,
            "物流号": p.get("logisticsNo") or "",
            "已创建小时": hours,
        })

    return rows


# =========================
# Django 调用入口（核心）
# =========================

def fetch_orders():
    """
    👇 Django 就调用这个
    """
    packages = fetch_packages()
    return build_rows(packages)


# =========================
# Excel 导出（脚本用）
# =========================

def export_excel(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "orders"

    headers = ["订单编号", "店铺", "区域", "时间", "物流号", "已创建小时"]

    for i, h in enumerate(headers, 1):
        ws.cell(1, i, h)

    for r, row in enumerate(rows, 2):
        for c, h in enumerate(headers, 1):
            ws.cell(r, c, row.get(h, ""))

    file = f"miaoshou_{int(time.time())}.xlsx"
    wb.save(file)
    print("已导出：", file)


# =========================
# CLI入口
# =========================

def main():
    rows = fetch_orders()
    export_excel(rows)
    print("完成，共", len(rows))


if __name__ == "__main__":
    main()
