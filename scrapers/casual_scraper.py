"""
休闲游戏详细分析数据处理
- 读取 data/casual_static.json 静态数据
- 输出 data/casual.json（供仪表盘读取）
"""

import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent.parent / "data"
STATIC_FILE = DATA_DIR / "casual_static.json"
OUTPUT_FILE = DATA_DIR / "casual.json"

REGION_NAMES = {
    "us": "美国", "gb": "英国", "de": "德国", "fr": "法国", "jp": "日本",
    "kr": "韩国", "id": "印尼", "th": "泰国", "sg": "新加坡", "vn": "越南"
}


def build_casual_data() -> dict:
    """从静态 JSON 构建休闲游戏分析数据"""
    static = json.loads(STATIC_FILE.read_text(encoding="utf-8"))
    regions_out = []
    for region_code, region_name in REGION_NAMES.items():
        s = static.get(region_code, {})
        regions_out.append({
            "region": region_code,
            "region_name": region_name,
            "top_games": s.get("top_games", []),
            "user_profile": s.get("user_profile", {}),
            "revenue_trend": s.get("revenue_trend", []),
            "insight": s.get("insight", ""),
        })
    return {
        "updated_at": static.get("updated_at", datetime.now(timezone.utc).strftime("%Y-%m")),
        "regions": regions_out,
    }


if __name__ == "__main__":
    print("[Casual Scraper] 开始处理休闲游戏数据...")
    data = build_casual_data()
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[Casual Scraper] 已写出 {OUTPUT_FILE}（{len(data['regions'])} 个地区）")
