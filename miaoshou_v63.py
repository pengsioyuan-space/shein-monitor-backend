# -*- coding: utf-8 -*-

import os
import json
import time
import hmac
import hashlib
import requests
from datetime import datetime, timedelta, timezone


# =========================
# 🔥 时间：近2天（你要的）
# =========================
def get_time_range(days=2):
    now = datetime.now()
    start = now - timedelta(days=days)
    end = now

    return (
        start.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )


ORDER_START_FROM, ORDER_START_TO = get_time_range(2)


# =========================
# 配置
# =========================
DOMAIN = "https://openapi-erp.91miaoshou.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(SCRIPT_DIR, "miaoshou_key.txt")

PAGE_SIZE = 100
PAGE_START = 1
MAX_PAGES = 1000


# =========================
# 读取 key
# =========================
def read_keys():
    data = {}
    with open(KEY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                data[k.lower()] = v.strip()

    return data["appkey"], data["appsecret"]


# =========================
# sign
# =========================
def sign(app_key, app_secret, path, ts, body):
    raw = f"{app_secret}{path}{ts}{app_key}{body}{app_secret}"
    return hmac.new(app_secret.encode(), raw.encode(), hashlib.sha256).hexdigest()


# =========================
# API 请求（已防崩）
# =========================
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

    try:
        r = requests.post(url, data=body_json.encode(), headers=headers, timeout=30)

        print("状态码:", r.status_code)
        print("返回前200:", r.text[:200])

        # ❗ 防空
        if not r.text or len(r.text.strip()) < 2:
            return None

        # ❗ 防 JSON 崩
        try:
            return r.json()
        except:
            print("❌ JSON解析失败")
            return None

    except Exception as e:
        print("❌ 请求失败:", e)
        return None


# =========================
# 拉包裹列表
# =========================
def fetch_packages():
    app_key, app_secret = read_keys()
    all_data = []

    for page in range(PAGE_START, PAGE_START + MAX_PAGES):

        body = {
            "page": page,
            "pageSize": PAGE_SIZE,
            "gmtCreateFrom": ORDER_START_FROM,
            "gmtCreateTo": ORDER_START_TO,
        }

        res = request_api(app_key, app_secret,
                           "/open/v1/order/package/fetch/search_package_list",
                           body)

        if not res:
            break

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
# 转业务数据
# =========================
def fetch_orders():
    try:
        packages = fetch_packages()

        if not packages:
            return []

        result = []

        for p in packages:
            result.append({
                "order_no": p.get("order_no") or p.get("orderSn") or "",
                "shop_name": p.get("shop_name", ""),
                "region": p.get("region", ""),
                "created_hours": p.get("created_hours", 0),
                "logistics_no": p.get("logistics_no", ""),
            })

        return result

    except Exception as e:
        print("❌ fetch_orders错误:", e)
        return []


# =========================
# CLI测试
# =========================
if __name__ == "__main__":
    data = fetch_orders()
    print("总数:", len(data))
