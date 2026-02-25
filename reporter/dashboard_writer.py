"""
数据导出模块
生成仪表盘所需的 JSON 文件：
- data/latest.json        榜单数据 + 元信息
- data/latest_changes.json 异动数据
- data/latest_analysis.json AI 分析文本
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"


def write_dashboard_json(
    chart_data: list[dict],
    changes: list[dict],
    ai_analysis: str,
    chart_summary: str,
    date_str: str,
):
    """生成仪表盘读取的三个 JSON 文件"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    regions = set(a.get("region_name") for a in chart_data)
    new_entries = sum(1 for c in changes if c.get("change_type") == "新进榜")

    # latest.json — 榜单数据
    latest = {
        "date": date_str,
        "total": len(chart_data),
        "regions": len(regions),
        "changes": len(changes),
        "new_entries": new_entries,
        "data": chart_data,
    }
    with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False)

    # latest_changes.json — 异动数据
    with open(DATA_DIR / "latest_changes.json", "w", encoding="utf-8") as f:
        json.dump({"date": date_str, "changes": changes}, f, ensure_ascii=False)

    # latest_analysis.json — AI 分析
    full_analysis = chart_summary + "\n\n" + ai_analysis
    with open(DATA_DIR / "latest_analysis.json", "w", encoding="utf-8") as f:
        json.dump({"date": date_str, "analysis": full_analysis}, f, ensure_ascii=False)

    print(f"[Dashboard] JSON 文件已生成到 data/")
