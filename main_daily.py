"""
主入口：每日榜单采集 + 新闻抓取 + 异动检测 + AI 分析 + 报告生成 + 推送
由 GitHub Actions 每天自动运行
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.appstore_scraper import fetch_all_appstore_charts
from scrapers.googleplay_scraper import fetch_all_googleplay_charts
from scrapers.news_scraper import fetch_all_news
from scrapers.change_detector import (
    load_chart_data, save_chart_data, detect_changes, get_top_movers
)
from analyzer.ai_analyzer import analyze_changes, generate_chart_summary_text
from reporter.excel_writer import write_daily_excel
from reporter.dashboard_writer import write_dashboard_json
from reporter.notifier import send_daily_wecom

UTC = timezone.utc


def run_daily():
    today     = datetime.now(UTC).strftime("%Y-%m-%d")
    yesterday = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")

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

    # ── 2. 抓取行业新闻 ──────────────────────────────────
    print("[Step 2] 抓取行业新闻...")
    news_list = fetch_all_news(hours=48)

    # ── 3. 保存今日 JSON ──────────────────────────────────
    print("\n[Step 3] 保存今日数据...")
    save_chart_data(all_data, today)

    # ── 4. 检测异动 ──────────────────────────────────────
    print("\n[Step 4] 检测榜单异动...")
    yesterday_data = load_chart_data(yesterday)
    if yesterday_data:
        changes    = detect_changes(all_data, yesterday_data)
        top_changes = get_top_movers(changes)
        print(f"  检测到 {len(changes)} 个异动，重点关注 {len(top_changes)} 个")
    else:
        changes     = []
        top_changes = []
        print("  无昨日数据，跳过异动检测（首次运行正常）")

    # ── 5. AI 分析（两部分）──────────────────────────────
    print("\n[Step 5] 生成 AI 分析...")
    chart_summary = generate_chart_summary_text(all_data)
    ai_analysis   = analyze_changes(top_changes, news_list=news_list)
    print(f"  榜单概要 {len(chart_summary)} 字，异动解读 {len(ai_analysis)} 字")

    # ── 6. 生成 Excel ────────────────────────────────────
    print("\n[Step 6] 生成 Excel 报告...")
    full_analysis = chart_summary + "\n\n" + ai_analysis
    excel_path = write_daily_excel(all_data, top_changes, full_analysis, today)
    print(f"  已输出：{excel_path}")

    # ── 7. 生成仪表盘 JSON ────────────────────────────────
    print("\n[Step 7] 生成仪表盘 JSON...")
    write_dashboard_json(all_data, top_changes, ai_analysis, chart_summary, today)

    # ── 8. 推送企业微信 ──────────────────────────────────
    print("\n[Step 8] 推送企业微信（两条）...")
    send_daily_wecom(all_data, top_changes, chart_summary, ai_analysis, today)

    print(f"\n{'='*50}")
    print("  每日采集完成！")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_daily()
