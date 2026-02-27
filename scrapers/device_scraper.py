"""
设备概况数据处理
- 读取 data/device_static.json 静态数据
- 输出 data/device.json（供仪表盘读取）
"""

import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent.parent / "data"
STATIC_FILE = DATA_DIR / "device_static.json"
OUTPUT_FILE = DATA_DIR / "device.json"

REGION_NAMES = {
    "us": "美国", "gb": "英国", "de": "德国", "fr": "法国", "jp": "日本",
    "kr": "韩国", "id": "印尼", "th": "泰国", "sg": "新加坡", "vn": "越南"
}


def build_device_data() -> dict:
    """从静态 JSON 构建设备数据"""
    static = json.loads(STATIC_FILE.read_text(encoding="utf-8"))
    regions_out = []
    for region_code, region_name in REGION_NAMES.items():
        s = static.get(region_code, {})
        regions_out.append({
            "region": region_code,
            "region_name": region_name,
            "ios_pct": s.get("ios_pct"),
            "android_pct": s.get("android_pct"),
            "top_devices": s.get("top_devices", []),
            "os_versions": s.get("os_versions", {}),
            "device_notes": s.get("device_notes", ""),
        })
    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "regions": regions_out,
    }


if __name__ == "__main__":
    print("[Device Scraper] 开始处理设备数据...")
    data = build_device_data()
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[Device Scraper] 已写出 {OUTPUT_FILE}（{len(data['regions'])} 个地区）")
