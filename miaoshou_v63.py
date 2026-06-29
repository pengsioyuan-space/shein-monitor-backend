import requests
import time
import json


# =========================
# 配置区（你只需要改这里）
# =========================
APP_KEY = "your_key"
APP_SECRET = "your_secret"

API_URL = "https://xxx.com/api"  # 妙手接口地址

ORDER_START_FROM = "2026-06-25 00:00:00"
ORDER_START_TO = "2026-06-27 23:59:59"


# =========================
# 网络请求层（稳定核心）
# =========================
def request_api(url, body, headers=None, retry=3):
    """
    稳定版请求：不会卡死 + 自动重试
    """

    headers = headers or {
        "Content-Type": "application/json"
    }

    for i in range(retry):
        try:
            print(f"📡 请求第 {i+1} 次: {url}")

            resp = requests.post(
                url,
                data=json.dumps(body),
                headers=headers,
                timeout=(5, 20)  # 连接5秒 + 响应20秒
            )

            print("✅ 状态码:", resp.status_code)

            if resp.status_code != 200:
                print("⚠️ 非200:", resp.text[:200])
                continue

            data = resp.json()

            if not data:
                print("⚠️ 空响应")
                continue

            return data

        except requests.exceptions.Timeout:
            print("⏰ 超时")
        except Exception as e:
            print("❌ 请求错误:", str(e))

        time.sleep(2)

    print("❌ 重试失败，返回空")
    return None


# =========================
# 获取包裹（核心）
# =========================
def fetch_packages():
    body = {
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "startTime": ORDER_START_FROM,
        "endTime": ORDER_START_TO
    }

    data = request_api(API_URL, body)

    if not data:
        return []

    return data.get("data", []) or []


# =========================
# 主入口
# =========================
def main():
    print("🚀 开始抓取订单...")

    packages = fetch_packages()

    print("📦 拉取数量:", len(packages))

    results = []

    for p in packages:
        try:
            results.append({
                "order_no": p.get("order_no"),
                "shop_name": p.get("shop_name"),
                "region": p.get("region"),
                "created_hours": p.get("created_hours"),
                "logistics_no": p.get("logistics_no")
            })
        except Exception as e:
            print("⚠️ 跳过异常数据:", e)

    print("✅ 处理完成:", len(results))

    return results
