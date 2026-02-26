"""
市场概况数据采集
- 从 World Bank Open Data API 拉取 4 个宏观指标
- 与 data/market_static.json 的静态数据合并
- 输出 data/market.json
"""

import json
import ssl
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

REGIONS = ["US", "GB", "DE", "FR", "JP", "KR", "ID", "TH", "SG", "VN"]
REGION_MAP = {  # World Bank 代码 → 项目 region 代码
    "US": "us", "GB": "gb", "DE": "de", "FR": "fr", "JP": "jp",
    "KR": "kr", "ID": "id", "TH": "th", "SG": "sg", "VN": "vn"
}
REGION_NAMES = {
    "us": "美国", "gb": "英国", "de": "德国", "fr": "法国", "jp": "日本",
    "kr": "韩国", "id": "印尼", "th": "泰国", "sg": "新加坡", "vn": "越南"
}

INDICATORS = {
    "IT.CEL.SETS.P2": "mobile_per_100",   # 手机普及率
    "IT.NET.USER.ZS": "internet_pct",      # 互联网渗透率
    "SP.POP.TOTL":    "population",        # 人口总数
    "NY.GDP.PCAP.CD": "gdp_per_capita",    # 人均 GDP (USD)
}

DATA_DIR = Path(__file__).parent.parent / "data"
STATIC_FILE = DATA_DIR / "market_static.json"
OUTPUT_FILE = DATA_DIR / "market.json"


def fetch_wb_indicator(indicator: str) -> dict:
    """从 World Bank API 拉取单个指标，返回 {country_code: value} 字典"""
    codes = ";".join(REGIONS)
    url = (
        f"https://api.worldbank.org/v2/country/{codes}"
        f"/indicator/{indicator}?format=json&mrv=1&per_page=20"
    )
    # 创建不验证证书的 SSL 上下文（macOS Python 需要）
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(url, timeout=15, context=ssl_context) as resp:
        raw = json.loads(resp.read().decode())
    result = {}
    if len(raw) >= 2 and raw[1]:
        for entry in raw[1]:
            code = entry["countryiso3code"] or entry["country"]["id"]
            # World Bank 返回3字母代码，需转换
            code2 = _iso3_to_iso2(code)
            if code2 and entry["value"] is not None:
                result[code2] = entry["value"]
    return result


_ISO3_MAP = {
    "USA": "US", "GBR": "GB", "DEU": "DE", "FRA": "FR", "JPN": "JP",
    "KOR": "KR", "IDN": "ID", "THA": "TH", "SGP": "SG", "VNM": "VN"
}

def _iso3_to_iso2(code3: str) -> str | None:
    return _ISO3_MAP.get(code3.upper())


def build_market_data() -> dict:
    static = json.loads(STATIC_FILE.read_text(encoding="utf-8"))

    # 拉取所有 World Bank 指标
    wb_data = {}
    for indicator, field in INDICATORS.items():
        print(f"  拉取 {indicator}...")
        values = fetch_wb_indicator(indicator)
        for iso2, val in values.items():
            key = REGION_MAP.get(iso2, iso2.lower())
            wb_data.setdefault(key, {})[field] = val

    # 合并静态 + 动态
    regions_out = []
    for region_code, region_name in REGION_NAMES.items():
        wb = wb_data.get(region_code, {})
        st = static.get(region_code, {})

        pop = wb.get("population", 0)
        mobile_rate = wb.get("mobile_per_100", 0)
        estimated_devices = int(pop * mobile_rate / 100) if pop and mobile_rate else None

        regions_out.append({
            "region": region_code,
            "region_name": region_name,
            "population": int(pop) if pop else None,
            "mobile_per_100": round(mobile_rate, 1) if mobile_rate else None,
            "internet_pct": round(wb.get("internet_pct", 0), 1) if wb.get("internet_pct") else None,
            "gdp_per_capita": int(wb.get("gdp_per_capita", 0)) if wb.get("gdp_per_capita") else None,
            "estimated_devices": estimated_devices,
            "genres": st.get("genres", []),
            "profile": st.get("profile", ""),
        })

    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "regions": regions_out,
    }


if __name__ == "__main__":
    print("[Market Scraper] 开始拉取市场数据...")
    data = build_market_data()
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[Market Scraper] 已写出 {OUTPUT_FILE}（{len(data['regions'])} 个地区）")
