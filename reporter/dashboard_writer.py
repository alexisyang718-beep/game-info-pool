"""
数据导出模块
生成仪表盘所需的 JSON 文件：
- data/latest.json          榜单数据 + 元信息
- data/latest_changes.json  异动数据
- data/latest_analysis.json AI 异动分析（结构化）
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"


def write_dashboard_json(
    chart_data: list[dict],
    changes: list[dict],
    ai_analysis: dict,
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

    # latest_analysis.json — AI 异动分析（结构化）
    # ai_analysis 现在是一个字典，包含 highlights, regions, categories, industry
    analysis_data = {
        "date": date_str,
        "highlights": ai_analysis.get("highlights", []) if isinstance(ai_analysis, dict) else [],
        "regions": ai_analysis.get("regions", "") if isinstance(ai_analysis, dict) else "",
        "categories": ai_analysis.get("categories", "") if isinstance(ai_analysis, dict) else "",
        "industry": ai_analysis.get("industry", "") if isinstance(ai_analysis, dict) else "",
    }
    
    # 兼容旧格式：如果 ai_analysis 是字符串，保存为 raw_text
    if isinstance(ai_analysis, str):
        analysis_data["raw_text"] = ai_analysis
    
    with open(DATA_DIR / "latest_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)

    print(f"[Dashboard] JSON 文件已生成到 data/")
