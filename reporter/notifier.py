"""
企业微信 & 邮件推送模块
"""

import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

WECOM_WEBHOOK_URL = os.environ.get("WECOM_WEBHOOK_URL", "")
EMAIL_SMTP_HOST = os.environ.get("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")


# ─── 企业微信推送 ────────────────────────────────────────────

def send_wecom_text(text: str):
    """发送纯文本消息到企业微信群"""
    if not WECOM_WEBHOOK_URL:
        print("[WeCom] 未配置 Webhook URL，跳过推送")
        return

    payload = {"msgtype": "text", "text": {"content": text}}
    try:
        resp = requests.post(WECOM_WEBHOOK_URL, json=payload, timeout=10)
        result = resp.json()
        if result.get("errcode") == 0:
            print("[WeCom] 推送成功")
        else:
            print(f"[WeCom] 推送失败: {result}")
    except Exception as e:
        print(f"[WeCom] 推送异常: {e}")


def send_wecom_markdown(markdown: str):
    """发送 Markdown 消息到企业微信群（最多4096字符）"""
    if not WECOM_WEBHOOK_URL:
        print("[WeCom] 未配置 Webhook URL，跳过推送")
        return

    # 企业微信 Markdown 限制 4096 字符，超出则截断
    if len(markdown) > 4000:
        markdown = markdown[:4000] + "\n\n...（内容已截断，请查看 Google Sheets 完整报告）"

    payload = {"msgtype": "markdown", "markdown": {"content": markdown}}
    try:
        resp = requests.post(WECOM_WEBHOOK_URL, json=payload, timeout=10)
        result = resp.json()
        if result.get("errcode") == 0:
            print("[WeCom] Markdown 推送成功")
        else:
            print(f"[WeCom] Markdown 推送失败: {result}")
    except Exception as e:
        print(f"[WeCom] 推送异常: {e}")


def build_daily_wecom_message(changes: list[dict], ai_analysis: str, date_str: str) -> str:
    """构建每日推送的企业微信消息"""
    # 取前10个重要异动
    top_changes = changes[:10]

    change_lines = []
    for c in top_changes:
        store = "AS" if c.get("store", "") != "google_play" else "GP"
        region = c.get("region_name", c.get("region", ""))
        change_type = c["change_type"]
        name = c["name"]

        if change_type == "新进榜":
            change_lines.append(f"> `{region}/{store}` 【新进榜】**{name}** #{c['rank_today']}")
        elif change_type == "退榜":
            change_lines.append(f"> `{region}/{store}` 【退榜】**{name}** (昨日#{c['rank_yesterday']})")
        else:
            arrow = "↑" if change_type == "上升" else "↓"
            delta = abs(c.get("rank_delta", 0))
            change_lines.append(
                f"> `{region}/{store}` 【{change_type}{delta}位{arrow}】**{name}** "
                f"#{c['rank_yesterday']}→#{c['rank_today']}"
            )

    change_text = "\n".join(change_lines) if change_lines else "> 今日无显著异动"

    # AI 分析截取前500字
    analysis_short = ai_analysis[:500] + "..." if len(ai_analysis) > 500 else ai_analysis

    message = f"""## 🎮 手游榜单日报 · {date_str}

**今日重点异动（共{len(changes)}个）**
{change_text}

---
**AI 市场解读**
{analysis_short}

---
📊 完整数据请查看 Google Sheets
"""
    return message


def build_weekly_wecom_message(weekly_summary: str, date_str: str) -> str:
    """构建每周推送的企业微信消息"""
    summary_short = weekly_summary[:1500] + "..." if len(weekly_summary) > 1500 else weekly_summary
    return f"""## 📈 手游市场周报 · {date_str}

{summary_short}

---
📊 完整周报请查看 Google Sheets
"""


# ─── 邮件推送 ────────────────────────────────────────────────

def send_email(subject: str, html_body: str):
    """发送 HTML 邮件"""
    if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
        print("[Email] 未完整配置邮件信息，跳过发送")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    part = MIMEText(html_body, "html", "utf-8")
    msg.attach(part)

    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO.split(","), msg.as_string())
        print(f"[Email] 邮件已发送至 {EMAIL_TO}")
    except Exception as e:
        print(f"[Email] 发送失败: {e}")


def markdown_to_html(md_text: str) -> str:
    """简单的 Markdown 转 HTML（避免引入额外依赖）"""
    import re
    html = md_text
    # 标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    # 粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # 列表
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # 换行
    html = html.replace('\n', '<br>\n')
    return f"<html><body style='font-family:sans-serif;max-width:800px;margin:auto;padding:20px'>{html}</body></html>"


def send_weekly_email(weekly_summary: str, date_str: str):
    """发送周报邮件"""
    subject = f"手游市场周报 · {date_str}"
    html = markdown_to_html(weekly_summary)
    send_email(subject, html)


if __name__ == "__main__":
    # 测试企业微信推送
    send_wecom_text("测试消息：手游信息池系统运行正常 ✓")
