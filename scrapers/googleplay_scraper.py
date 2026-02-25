"""
Google Play 榜单爬虫
调用 scrapers/googleplay_scraper.js（Node.js）获取数据
"""

import json
import subprocess
from pathlib import Path


JS_SCRIPT = Path(__file__).parent / "googleplay_scraper.js"


def fetch_all_googleplay_charts() -> list[dict]:
    """调用 Node.js 脚本拉取所有地区 Google Play 榜单"""
    try:
        result = subprocess.run(
            ["node", str(JS_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=300,  # 最多等5分钟
        )
        # stderr 是进度日志，打印出来
        if result.stderr:
            print(result.stderr, end="")

        if result.returncode != 0:
            print(f"[GooglePlay] Node.js 脚本异常退出 code={result.returncode}")
            return []

        data = json.loads(result.stdout)
        return data

    except subprocess.TimeoutExpired:
        print("[GooglePlay] 超时，跳过")
        return []
    except Exception as e:
        print(f"[GooglePlay] 调用失败: {e}")
        return []


if __name__ == "__main__":
    data = fetch_all_googleplay_charts()
    print(f"\n总计获取 {len(data)} 条记录")
    for item in data[:3]:
        print(f"  [{item['region_name']}] #{item['rank']} {item['name']} - {item['artist']}")
