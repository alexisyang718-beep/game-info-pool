"""
App Store 榜单爬虫
使用苹果 iTunes RSS API（稳定，官方支持）
"""

import requests
from datetime import datetime, timezone
from datetime import timezone as tz
import time

UTC = timezone.utc

# 目标地区配置
REGIONS = {
    "us": "美国",
    "gb": "英国",
    "de": "德国",
    "fr": "法国",
    "jp": "日本",
    "kr": "韩国",
    "id": "印度尼西亚",
    "th": "泰国",
    "sg": "新加坡",
    "vn": "越南",
}

# 榜单类型（iTunes RSS API 格式）
CHART_TYPES = {
    "topfreeapplications": "免费游戏榜",
    "toppaidapplications": "付费游戏榜",
    "topgrossingapplications": "畅销榜",
}

GAME_GENRE_ID = "6014"


def fetch_appstore_chart(region: str, chart_type: str, limit: int = 100) -> list[dict]:
    """
    从苹果 iTunes RSS API 拉取榜单
    接口：https://itunes.apple.com/{country}/rss/{chart}/limit={n}/genre=6014/json
    """
    url = (
        f"https://itunes.apple.com/{region}/rss/{chart_type}"
        f"/limit={limit}/genre={GAME_GENRE_ID}/json"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        entries = data.get("feed", {}).get("entry", [])

        apps = []
        for rank, entry in enumerate(entries, start=1):
            # link 字段可能是 dict 或 list，统一处理
            link_field = entry.get("link", {})
            if isinstance(link_field, list):
                link_field = link_field[0] if link_field else {}
            url = link_field.get("attributes", {}).get("href", "")

            apps.append({
                "rank": rank,
                "app_id": entry.get("id", {}).get("attributes", {}).get("im:id", ""),
                "name": entry.get("im:name", {}).get("label", ""),
                "artist": entry.get("im:artist", {}).get("label", ""),
                "genre": entry.get("category", {}).get("attributes", {}).get("label", ""),
                "genre_id": entry.get("category", {}).get("attributes", {}).get("im:id", ""),
                "url": url,
                "artwork": entry.get("im:image", [{}])[-1].get("label", ""),
                "price": entry.get("im:price", {}).get("label", ""),
                "release_date": entry.get("im:releaseDate", {}).get("label", ""),
                "region": region,
                "region_name": REGIONS.get(region, region),
                "chart_type": chart_type,
                "chart_name": CHART_TYPES.get(chart_type, chart_type),
                "store": "appstore",
                "fetch_date": datetime.now(UTC).strftime("%Y-%m-%d"),
                "fetch_ts": datetime.now(UTC).isoformat(),
            })
        return apps

    except Exception as e:
        print(f"[AppStore] 拉取失败 region={region} chart={chart_type}: {e}")
        return []


def fetch_all_appstore_charts() -> list[dict]:
    """拉取所有地区、所有榜单类型"""
    all_data = []
    for region in REGIONS:
        for chart_type in CHART_TYPES:
            print(f"[AppStore] 正在拉取 {REGIONS[region]} {CHART_TYPES[chart_type]}...")
            apps = fetch_appstore_chart(region, chart_type)
            all_data.extend(apps)
            print(f"  → 获取 {len(apps)} 条")
            time.sleep(0.5)
    return all_data


if __name__ == "__main__":
    data = fetch_all_appstore_charts()
    print(f"\n总计获取 {len(data)} 条记录")
    for item in data[:5]:
        print(f"  [{item['region_name']}] #{item['rank']} {item['name']} - {item['artist']}")
