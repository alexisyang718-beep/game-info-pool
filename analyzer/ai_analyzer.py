"""
AI 异动解读模块
使用 MiniMax API 分析榜单异动原因
"""

import os
import json
import requests
from datetime import datetime


MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"


def call_minimax(prompt: str, system_prompt: str = "") -> str:
    """调用 MiniMax API"""
    if not MINIMAX_API_KEY:
        return "[未配置 MINIMAX_API_KEY，跳过 AI 分析]"

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "abab6.5s-chat",
        "messages": [
            {"role": "system", "content": system_prompt or "你是一位专业的手游市场分析师。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
        "max_tokens": 1500,
    }
    try:
        resp = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[AI 分析失败: {e}]"


def analyze_changes(changes: list[dict]) -> str:
    """
    对榜单异动进行 AI 解读
    输入：异动列表
    输出：分析报告文字
    """
    if not changes:
        return "今日暂无显著榜单异动。"

    # 整理异动数据为可读格式
    lines = []
    for c in changes[:30]:  # 最多分析30条，避免 token 过多
        region = c.get("region_name", c.get("region", ""))
        store = "App Store" if c.get("store", "") != "google_play" else "Google Play"
        change_type = c["change_type"]
        name = c["name"]
        artist = c.get("artist", "")

        if change_type == "新进榜":
            lines.append(f"- {region}/{store}: 《{name}》({artist}) 新进榜，当前排名 #{c['rank_today']}")
        elif change_type == "退榜":
            lines.append(f"- {region}/{store}: 《{name}》({artist}) 退榜（昨日 #{c['rank_yesterday']}）")
        elif change_type in ("上升", "下降"):
            delta = abs(c.get("rank_delta", 0))
            lines.append(
                f"- {region}/{store}: 《{name}》({artist}) {change_type} {delta} 位"
                f"（昨日 #{c['rank_yesterday']} → 今日 #{c['rank_today']}）"
            )

    changes_text = "\n".join(lines)
    today = datetime.utcnow().strftime("%Y年%m月%d日")

    prompt = f"""
以下是 {today} 的手游榜单异动数据（覆盖美国、英国、德国、法国、日本、韩国、印尼、泰国、新加坡、越南市场）：

{changes_text}

请从以下角度进行专业解读（约500字）：
1. **重点异动**：挑选最值得关注的3-5个异动进行点评
2. **可能原因**：分析每个重点异动的可能原因（版本更新、买量加大、节假日/赛事营销、竞品下架、品类趋势等）
3. **地区规律**：有哪些值得注意的地区性特征
4. **品类趋势**：从今日异动能看出哪些品类在走强或走弱

输出格式：中文，使用 Markdown，段落清晰。
"""

    system = "你是一位拥有10年经验的手游市场分析师，熟悉全球各地区手游市场特征、买量策略和产品生命周期规律。请基于数据给出专业、务实的分析。"

    return call_minimax(prompt, system)


def generate_weekly_summary(all_week_changes: list[dict], top_charts: list[dict]) -> str:
    """生成周报摘要"""
    # 统计本周异动频率最高的游戏
    from collections import Counter
    app_counter = Counter(c["name"] for c in all_week_changes)
    top_movers = app_counter.most_common(10)

    movers_text = "\n".join([f"- 《{name}》: 出现 {count} 次异动" for name, count in top_movers])

    # 各地区 Top3 游戏
    region_tops = {}
    for app in top_charts:
        region = app.get("region_name", app.get("region", ""))
        if region not in region_tops:
            region_tops[region] = []
        if app["rank"] <= 3:
            region_tops[region].append(f"#{app['rank']} {app['name']}")

    region_text = ""
    for region, tops in region_tops.items():
        region_text += f"\n**{region}**: {', '.join(tops)}"

    prompt = f"""
请基于以下本周手游市场数据，生成一份简洁的**周报摘要**（约800字）：

**本周异动最频繁的游戏（上榜/下榜/大幅波动次数）：**
{movers_text}

**各地区当前 Top3 游戏：**
{region_text}

请输出：
1. **本周市场总结**（整体趋势，2-3段）
2. **重点关注产品**（3-5款值得持续跟踪的游戏及原因）
3. **下周预判**（基于当前趋势的合理预测）

语言：中文，Markdown 格式，适合发送给游戏公司产品/市场团队阅读。
"""
    system = "你是一位专业的手游市场周报分析师，为游戏公司产品和市场团队提供市场洞察。"
    return call_minimax(prompt, system)


if __name__ == "__main__":
    # 测试
    test_changes = [
        {
            "name": "Royal Match",
            "artist": "Dream Games",
            "region": "us",
            "region_name": "美国",
            "store": "appstore",
            "chart_name": "免费游戏榜",
            "change_type": "上升",
            "rank_today": 3,
            "rank_yesterday": 15,
            "rank_delta": 12,
        }
    ]
    result = analyze_changes(test_changes)
    print(result)
