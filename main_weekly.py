"""
主入口：每周报告生成与推送
每周一 UTC 01:00（北京时间 09:00）运行
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

from scrapers.change_detector import load_chart_data, detect_changes, get_top_movers
from analyzer.ai_analyzer import generate_weekly_summary
from reporter.excel_writer import write_weekly_excel
from reporter.notifier import send_wecom_markdown, build_weekly_wecom_message, send_weekly_email


def run_weekly():
    today = datetime.utcnow().strftime("%Y-%m-%d")

    print(f"\n{'='*50}")
    print(f"  手游信息池 · 周报生成  {today}")
    print(f"{'='*50}\n")

    # ── 收集过去7天的异动数据 ────────────────────────────
    print("[Step 1] 收集过去7天异动数据...")
    all_week_changes = []
    latest_data = []

    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        prev_date = (datetime.utcnow() - timedelta(days=i + 1)).strftime("%Y-%m-%d")

        today_data = load_chart_data(date)
        yesterday_data = load_chart_data(prev_date)

        if today_data and yesterday_data:
            changes = detect_changes(today_data, yesterday_data)
            all_week_changes.extend(changes)

        if i == 0 and today_data:
            latest_data = today_data

    print(f"  本周共 {len(all_week_changes)} 个异动事件")

    # ── 生成 AI 周报 ─────────────────────────────────────
    print("\n[Step 2] AI 生成周报...")
    weekly_summary = generate_weekly_summary(all_week_changes, latest_data)
    print(f"  周报生成完成（{len(weekly_summary)} 字）")

    # ── 生成 Excel ───────────────────────────────────────
    print("\n[Step 3] 生成 Excel 周报...")
    excel_path = write_weekly_excel(all_week_changes, latest_data, weekly_summary, today)
    print(f"  已输出：{excel_path}")

    # ── 推送 ─────────────────────────────────────────────
    print("\n[Step 4] 推送周报...")
    wecom_msg = build_weekly_wecom_message(weekly_summary, today)
    send_wecom_markdown(wecom_msg)
    send_weekly_email(weekly_summary, today)

    print(f"\n{'='*50}")
    print("  周报完成！")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_weekly()
