"""
主入口：每日榜单采集 + 异动检测 + AI 分析 + 推送
由 GitHub Actions 每天自动运行
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.appstore_scraper import fetch_all_appstore_charts
from scrapers.googleplay_scraper import fetch_all_googleplay_charts
from scrapers.change_detector import (
    load_chart_data, save_chart_data, detect_changes, get_top_movers
)
from analyzer.ai_analyzer import analyze_changes
from reporter.excel_writer import write_daily_excel
from reporter.notifier import send_wecom_markdown, build_daily_wecom_message


def run_daily():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"\n{'='*50}")
    print(f"  手游信息池 · 每日采集  {today}")
    print(f"{'='*50}\n")

    # ── 1. 采集榜单 ──────────────────────────────────────
    print("[Step 1] 采集 App Store 榜单...")
    appstore_data = fetch_all_appstore_charts()
    for app in appstore_data:
        app["store"] = "appstore"
    print(f"  App Store 共 {len(appstore_data)} 条\n")

    print("[Step 1] 采集 Google Play 榜单...")
    gplay_data = fetch_all_googleplay_charts()
    print(f"  Google Play 共 {len(gplay_data)} 条\n")

    all_data = appstore_data + gplay_data

    # ── 2. 保存今日 JSON（用于异动对比）────────────────────
    print("[Step 2] 保存今日数据...")
    save_chart_data(all_data, today)

    # ── 3. 检测异动 ──────────────────────────────────────
    print("\n[Step 3] 检测榜单异动...")
    yesterday_data = load_chart_data(yesterday)
    if yesterday_data:
        changes = detect_changes(all_data, yesterday_data)
        top_changes = get_top_movers(changes)
        print(f"  检测到 {len(changes)} 个异动，重点关注 {len(top_changes)} 个")
    else:
        changes = []
        top_changes = []
        print("  无昨日数据，跳过异动检测（首次运行正常）")

    # ── 4. AI 分析 ───────────────────────────────────────
    print("\n[Step 4] AI 异动解读...")
    ai_analysis = analyze_changes(top_changes)
    print(f"  AI 分析完成（{len(ai_analysis)} 字）")

    # ── 5. 生成 Excel ────────────────────────────────────
    print("\n[Step 5] 生成 Excel 报告...")
    excel_path = write_daily_excel(all_data, top_changes, ai_analysis, today)
    print(f"  已输出：{excel_path}")

    # ── 6. 推送企业微信 ──────────────────────────────────
    print("\n[Step 6] 推送企业微信...")
    wecom_msg = build_daily_wecom_message(top_changes, ai_analysis, today)
    send_wecom_markdown(wecom_msg)

    print(f"\n{'='*50}")
    print("  每日采集完成！")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_daily()
