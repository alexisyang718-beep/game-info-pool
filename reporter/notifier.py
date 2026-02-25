"""
企业微信 & 邮件推送模块
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

WECOM_WEBHOOK_URL = os.environ.get("WECOM_WEBHOOK_URL", "")
GITHUB_PAGES_URL  = os.environ.get("GITHUB_PAGES_URL", "")   # 仪表盘链接，在 Secrets 配置
EMAIL_SMTP_HOST = os.environ.get("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
EMAIL_TO   = os.environ.get("EMAIL_TO", "")


# ─── 企业微信核心发送 ──────────────────────────────────────

def _send_markdown(markdown: str):
    """发送 Markdown 到企业微信（内部函数）"""
    if not WECOM_WEBHOOK_URL:
        print("[WeCom] 未配置 Webhook URL，跳过推送")
        return
    # 企业微信单条 Markdown 上限 4096 字符
    if len(markdown) > 4000:
        markdown = markdown[:3980] + "\n\n...（内容已截断）"
    payload = {"msgtype": "markdown", "markdown": {"content": markdown}}
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
    """对外接口：发送 Markdown"""
    _send_markdown(markdown)


def send_wecom_text(text: str):
    payload = {"msgtype": "text", "text": {"content": text}}
    if not WECOM_WEBHOOK_URL:
        return
    try:
        requests.post(WECOM_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[WeCom] 推送异常: {e}")


# ─── 每日推送：两条消息 ────────────────────────────────────

def send_daily_wecom(
    chart_data: list[dict],
    changes: list[dict],
    chart_summary: str,
    ai_analysis: str,
    date_str: str,
):
    """
    每日推送分两条发送：
    第一条：榜单概要（各渠道 Top5 表格）
    第二条：异动解读 + 仪表盘链接
    """
    dashboard_link = GITHUB_PAGES_URL or ""
    link_line = f"\n\n[📊 查看完整仪表盘]({dashboard_link})" if dashboard_link else ""

    # ── 第一条：榜单概要（畅销榜 Top3，控制在 4000 字内）──
    from collections import defaultdict
    REGION_ORDER = ["美国", "日本", "韩国", "英国", "德国", "法国",
                    "印度尼西亚", "泰国", "新加坡", "越南"]

    # 按 (store, region) 取畅销榜 Top3
    gross_groups = defaultdict(list)
    for app in chart_data:
        if app.get("chart_name") == "畅销榜":
            key = (app.get("store", ""), app.get("region_name", ""))
            gross_groups[key].append(app)

    as_lines = []
    gp_lines = []
    for region in REGION_ORDER:
        # App Store
        as_apps = sorted(gross_groups.get(("appstore", region), []),
                         key=lambda x: x.get("rank", 999))[:3]
        if as_apps:
            top3 = " / ".join([f"#{a['rank']}{a['name']}" for a in as_apps])
            as_lines.append(f"> `{region}` {top3}")
        # Google Play
        gp_apps = sorted(gross_groups.get(("google_play", region), []),
                         key=lambda x: x.get("rank", 999))[:3]
        if gp_apps:
            top3 = " / ".join([f"#{a['rank']}{a['name']}" for a in gp_apps])
            gp_lines.append(f"> `{region}` {top3}")

    total = len(chart_data)
    regions_count = len(set(a.get("region_name") for a in chart_data))

    msg1 = (
        f"## 🎮 手游榜单日报 · {date_str}（一）榜单概要\n\n"
        f"**数据概览**：{total} 条 · {regions_count} 地区 · AS+GP · 完整数据见仪表盘{link_line}\n\n"
        f"**App Store 畅销榜 Top3**\n" + "\n".join(as_lines) +
        f"\n\n**Google Play 畅销榜 Top3**\n" + "\n".join(gp_lines)
    )
    _send_markdown(msg1)

    # ── 第二条：异动解读 ──────────────────────────────────
    change_lines = []
    for c in changes[:12]:
        store = "AS" if c.get("store", "") != "google_play" else "GP"
        region = c.get("region_name", "")
        change_type = c["change_type"]
        name = c["name"]
        if change_type == "新进榜":
            change_lines.append(f"> `{region}/{store}` **【新进榜】{name}** #{c['rank_today']}")
        elif change_type == "退榜":
            change_lines.append(f"> `{region}/{store}` **【退榜】{name}** 昨日#{c['rank_yesterday']}")
        else:
            arrow = "↑" if change_type == "上升" else "↓"
            delta = abs(c.get("rank_delta", 0))
            change_lines.append(
                f"> `{region}/{store}` **{name}** {change_type}{delta}位{arrow} "
                f"#{c['rank_yesterday']}→#{c['rank_today']}"
            )

    change_text = "\n".join(change_lines) if change_lines else "> 今日无显著异动（首次运行或数据未更新）"

    # AI 分析取第二部分（## 第二部分 之后的内容）
    if "第二部分" in ai_analysis:
        ai_short = ai_analysis[ai_analysis.index("第二部分"):]
    else:
        ai_short = ai_analysis
    ai_short = ai_short[:1200] + ("..." if len(ai_short) > 1200 else "")

    msg2 = f"""## 🎮 手游榜单日报 · {date_str}（二）异动解读

**今日异动（共{len(changes)}个）**
{change_text}

---
{ai_short}{link_line}
"""
    _send_markdown(msg2)


# ─── 周报推送 ──────────────────────────────────────────────

def build_weekly_wecom_message(weekly_summary: str, date_str: str) -> str:
    dashboard_link = GITHUB_PAGES_URL or ""
    link_line = f"\n\n[📊 查看完整仪表盘]({dashboard_link})" if dashboard_link else ""
    summary_short = weekly_summary[:1500] + "..." if len(weekly_summary) > 1500 else weekly_summary
    return f"""## 📈 手游市场周报 · {date_str}

{summary_short}{link_line}
"""


# ─── 邮件推送 ──────────────────────────────────────────────

def _markdown_to_html(md_text: str) -> str:
    import re
    html = md_text
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = html.replace('\n', '<br>\n')
    return (
        "<html><body style='font-family:sans-serif;max-width:800px;margin:auto;padding:20px'>"
        + html + "</body></html>"
    )


def send_email(subject: str, html_body: str):
    if not all([EMAIL_USER, EMAIL_PASS, EMAIL_TO]):
        print("[Email] 未完整配置邮件信息，跳过")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_USER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
            server.ehlo(); server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO.split(","), msg.as_string())
        print(f"[Email] 已发送至 {EMAIL_TO}")
    except Exception as e:
        print(f"[Email] 发送失败: {e}")


def send_weekly_email(weekly_summary: str, date_str: str):
    send_email(f"手游市场周报 · {date_str}", _markdown_to_html(weekly_summary))
