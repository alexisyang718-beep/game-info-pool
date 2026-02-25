"""
App Store 榜单爬虫
使用苹果官方 RSS API，完全合法，无需额外权限
"""

import requests
import json
from datetime import datetime

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

# 榜单类型
CHART_TYPES = {
    "topfreeapplications": "免费游戏榜",
    "toppaidapplications": "付费游戏榜",
}

GAME_GENRE_ID = "6014"  # App Store 游戏品类 ID


def fetch_appstore_chart(region: str, chart_type: str, limit: int = 100) -> list[dict]:
    """
    从苹果官方 RSS API 拉取榜单
    文档：https://rss.applemarketingtools.com
    """
    url = (
        f"https://rss.applemarketingtools.com/api/v2/{region}/apps/"
        f"{chart_type}/{limit}/apps.json"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("feed", {}).get("results", [])

        apps = []
        for rank, app in enumerate(results, start=1):
            apps.append({
                "rank": rank,
                "app_id": app.get("id"),
                "name": app.get("name"),
                "artist": app.get("artistName"),
                "genre": app.get("genres", [{}])[0].get("name", "") if app.get("genres") else "",
                "genre_id": app.get("genres", [{}])[0].get("genreId", "") if app.get("genres") else "",
                "url": app.get("url"),
                "artwork": app.get("artworkUrl100"),
                "release_date": app.get("releaseDate"),
                "region": region,
                "region_name": REGIONS.get(region, region),
                "chart_type": chart_type,
                "chart_name": CHART_TYPES.get(chart_type, chart_type),
                "fetch_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "fetch_ts": datetime.utcnow().isoformat(),
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
            # 只保留游戏品类（部分接口可能混入非游戏）
            games = [a for a in apps if a["genre_id"] == GAME_GENRE_ID or "game" in a["genre"].lower() or "游戏" in a["genre"]]
            # 如果过滤后太少，保留原始数据（说明本来就是游戏榜）
            all_data.extend(games if len(games) > 20 else apps)
            print(f"  → 获取 {len(apps)} 条，游戏 {len(games)} 条")
    return all_data


if __name__ == "__main__":
    data = fetch_all_appstore_charts()
    print(f"\n总计获取 {len(data)} 条记录")
    # 测试输出前3条
    for item in data[:3]:
        print(f"  [{item['region_name']}] #{item['rank']} {item['name']}")
