"""
Google Play 榜单爬虫
使用 Google Play 公开 RSS XML 接口获取榜单数据
接口文档：https://play.google.com/store/apps/collection/...
"""

import requests
import re
from datetime import datetime
import time

# 目标地区配置
REGIONS = {
    "us": {"country": "us", "lang": "en", "name": "美国"},
    "gb": {"country": "gb", "lang": "en", "name": "英国"},
    "de": {"country": "de", "lang": "de", "name": "德国"},
    "fr": {"country": "fr", "lang": "fr", "name": "法国"},
    "jp": {"country": "jp", "lang": "ja", "name": "日本"},
    "kr": {"country": "kr", "lang": "ko", "name": "韩国"},
    "id": {"country": "id", "lang": "id", "name": "印度尼西亚"},
    "th": {"country": "th", "lang": "th", "name": "泰国"},
    "sg": {"country": "sg", "lang": "en", "name": "新加坡"},
    "vn": {"country": "vn", "lang": "vi", "name": "越南"},
}

CHART_CONFIGS = [
    {"collection": "topselling_free",   "name": "免费游戏榜"},
    {"collection": "topselling_paid",   "name": "付费游戏榜"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_googleplay_chart(region_code: str, collection: str, chart_name: str, limit: int = 100) -> list[dict]:
    """通过 Google Play RSS 接口拉取榜单"""
    region_info = REGIONS[region_code]
    hl = region_info["lang"]
    gl = region_info["country"]

    url = (
        f"https://play.google.com/store/apps/collection/{collection}"
        f"?hl={hl}&gl={gl}&num={limit}"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        html = resp.text

        # 从页面中提取 app ID 和名称
        # Google Play 页面中 app ID 格式：?id=com.xxx.xxx
        app_ids = re.findall(r'href="/store/apps/details\?id=([^"&]+)"', html)
        # 提取 app 名称（aria-label 属性）
        app_names = re.findall(r'aria-label="([^"]+)"', html)

        if not app_ids:
            raise ValueError("未找到应用数据，页面可能已变更")

        # 去重保持顺序
        seen = set()
        unique_ids = []
        for aid in app_ids:
            if aid not in seen and not aid.startswith("?"):
                seen.add(aid)
                unique_ids.append(aid)

        apps = []
        for rank, app_id in enumerate(unique_ids[:limit], start=1):
            # 简单处理名称：从 app_id 末段提取可读名
            readable_name = app_id.split(".")[-1].replace("_", " ").title()
            apps.append({
                "rank": rank,
                "app_id": app_id,
                "name": readable_name,
                "artist": "",
                "genre": "GAME",
                "genre_id": "GAME",
                "url": f"https://play.google.com/store/apps/details?id={app_id}",
                "artwork": "",
                "score": None,
                "ratings": None,
                "installs": None,
                "price": 0,
                "region": region_code,
                "region_name": region_info["name"],
                "chart_type": collection,
                "chart_name": chart_name,
                "store": "google_play",
                "fetch_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "fetch_ts": datetime.utcnow().isoformat(),
            })

        return apps

    except Exception as e:
        print(f"[GooglePlay] 拉取失败 region={region_code} chart={chart_name}: {e}")
        return []


def fetch_all_googleplay_charts() -> list[dict]:
    """拉取所有地区、所有榜单类型"""
    all_data = []
    for region_code in REGIONS:
        for cfg in CHART_CONFIGS:
            region_name = REGIONS[region_code]["name"]
            print(f"[GooglePlay] 正在拉取 {region_name} {cfg['name']}...")
            apps = fetch_googleplay_chart(region_code, cfg["collection"], cfg["name"])
            all_data.extend(apps)
            print(f"  → 获取 {len(apps)} 条")
            time.sleep(2)
    return all_data


if __name__ == "__main__":
    data = fetch_all_googleplay_charts()
    print(f"\n总计获取 {len(data)} 条记录")
    for item in data[:3]:
        print(f"  [{item['region_name']}] #{item['rank']} {item['name']}")
