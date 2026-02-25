"""
Google Play 榜单爬虫
使用 google-play-scraper 开源库
"""

from google_play_scraper import chart, Collection, Category
from datetime import datetime
import time

# 目标地区配置（Google Play 用语言-国家代码）
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

# 榜单类型
CHART_CONFIGS = [
    {"collection": Collection.TOP_FREE, "name": "免费游戏榜"},
    {"collection": Collection.TOP_PAID, "name": "付费游戏榜"},
]


def fetch_googleplay_chart(region_code: str, collection: str, chart_name: str, limit: int = 100) -> list[dict]:
    """拉取 Google Play 单个地区榜单"""
    region_info = REGIONS[region_code]
    try:
        result = chart(
            country=region_info["country"],
            lang=region_info["lang"],
            category=Category.GAME,
            collection=collection,
            count=limit,
        )
        apps = []
        for rank, app in enumerate(result, start=1):
            apps.append({
                "rank": rank,
                "app_id": app.get("appId"),
                "name": app.get("title"),
                "artist": app.get("developer"),
                "genre": app.get("genre", ""),
                "genre_id": app.get("genreId", ""),
                "url": f"https://play.google.com/store/apps/details?id={app.get('appId')}",
                "artwork": app.get("icon"),
                "score": app.get("score"),
                "ratings": app.get("ratings"),
                "installs": app.get("installs"),
                "price": app.get("price", 0),
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
            time.sleep(1)  # 避免请求过快
    return all_data


if __name__ == "__main__":
    data = fetch_all_googleplay_charts()
    print(f"\n总计获取 {len(data)} 条记录")
    for item in data[:3]:
        print(f"  [{item['region_name']}] #{item['rank']} {item['name']}")
