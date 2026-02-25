"""
榜单异动检测模块
对比今日和昨日榜单，找出新进榜、上升、下降、退榜的应用
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "history"


def load_chart_data(date_str: str) -> list[dict]:
    """读取指定日期的榜单数据"""
    filepath = DATA_DIR / f"{date_str}.json"
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chart_data(data: list[dict], date_str: str):
    """保存榜单数据到 JSON 文件"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / f"{date_str}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Storage] 已保存 {len(data)} 条记录到 {filepath}")


def detect_changes(today_data: list[dict], yesterday_data: list[dict]) -> list[dict]:
    """
    检测榜单异动
    返回格式：[{app_id, name, region, store, chart_type, change_type, rank_today, rank_yesterday, rank_delta}]
    """
    changes = []

    # 按 (store, region, chart_type) 分组处理
    groups = {}
    for app in today_data:
        key = (app.get("store", "appstore"), app["region"], app["chart_type"])
        groups.setdefault(key, {"today": [], "yesterday": []})
        groups[key]["today"].append(app)

    for app in yesterday_data:
        key = (app.get("store", "appstore"), app["region"], app["chart_type"])
        if key in groups:
            groups[key]["yesterday"].append(app)

    for (store, region, chart_type), group in groups.items():
        today_map = {a["app_id"]: a for a in group["today"]}
        yesterday_map = {a["app_id"]: a for a in group["yesterday"]}

        today_ids = set(today_map.keys())
        yesterday_ids = set(yesterday_map.keys())

        # 新进榜
        for app_id in today_ids - yesterday_ids:
            app = today_map[app_id]
            changes.append({
                "app_id": app_id,
                "name": app["name"],
                "artist": app.get("artist", ""),
                "region": region,
                "region_name": app.get("region_name", region),
                "store": store,
                "chart_type": chart_type,
                "chart_name": app.get("chart_name", ""),
                "change_type": "新进榜",
                "rank_today": app["rank"],
                "rank_yesterday": None,
                "rank_delta": None,
            })

        # 退榜
        for app_id in yesterday_ids - today_ids:
            app = yesterday_map[app_id]
            changes.append({
                "app_id": app_id,
                "name": app["name"],
                "artist": app.get("artist", ""),
                "region": region,
                "region_name": app.get("region_name", region),
                "store": store,
                "chart_type": chart_type,
                "chart_name": app.get("chart_name", ""),
                "change_type": "退榜",
                "rank_today": None,
                "rank_yesterday": app["rank"],
                "rank_delta": None,
            })

        # 排名变化（上升/下降超过5位）
        for app_id in today_ids & yesterday_ids:
            today_rank = today_map[app_id]["rank"]
            yesterday_rank = yesterday_map[app_id]["rank"]
            delta = yesterday_rank - today_rank  # 正数=上升，负数=下降

            if abs(delta) >= 5:
                app = today_map[app_id]
                changes.append({
                    "app_id": app_id,
                    "name": app["name"],
                    "artist": app.get("artist", ""),
                    "region": region,
                    "region_name": app.get("region_name", region),
                    "store": store,
                    "chart_type": chart_type,
                    "chart_name": app.get("chart_name", ""),
                    "change_type": "上升" if delta > 0 else "下降",
                    "rank_today": today_rank,
                    "rank_yesterday": yesterday_rank,
                    "rank_delta": delta,
                })

    # 按变化幅度排序
    changes.sort(key=lambda x: abs(x.get("rank_delta") or 0), reverse=True)
    return changes


def get_top_movers(changes: list[dict], top_n: int = 20) -> list[dict]:
    """获取最值得关注的异动（新进榜Top10 + 变化最大的）"""
    new_entries = [c for c in changes if c["change_type"] == "新进榜"][:top_n]
    big_movers = [c for c in changes if c["change_type"] in ("上升", "下降")][:top_n]
    return new_entries + big_movers


if __name__ == "__main__":
    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    today_data = load_chart_data(today)
    yesterday_data = load_chart_data(yesterday)

    if not yesterday_data:
        print("没有昨日数据，无法计算异动")
    else:
        changes = detect_changes(today_data, yesterday_data)
        print(f"检测到 {len(changes)} 个异动")
        for c in changes[:5]:
            print(f"  [{c['region_name']}] {c['name']} - {c['change_type']} "
                  f"(今日#{c['rank_today']} 昨日#{c['rank_yesterday']})")
