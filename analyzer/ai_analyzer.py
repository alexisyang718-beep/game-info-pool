"""
AI 分析模块
使用 MiniMax API 生成结构化的异动分析报告：
- 上升异动：排名显著上升的游戏
- 下降异动：排名显著下降的游戏
- 新进榜：新上榜的游戏
- 地区趋势：各地区规律或差异
- 品类动向：品类走势分析
- 行业动态：相关行业背景
"""

import os
import json
import requests
from collections import defaultdict
from datetime import datetime

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
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
        "max_tokens": 2000,
    }
    try:
        resp = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[AI 分析失败: {e}]"


def build_chart_summary(chart_data: list[dict]) -> str:
    """
    构建第一部分：各渠道 Top5 榜单概要文本（供 AI 扩写）
    格式：地区 > 榜单类型 > Top5
    """
    # 按 (store, chart_name, region_name) 分组，取 Top5
    groups = defaultdict(list)
    for app in chart_data:
        key = (app.get("store", "appstore"), app.get("chart_name", ""), app.get("region_name", ""))
        groups[key].append(app)

    lines = []
    # 按商店、榜单类型、地区排序输出
    store_order = {"appstore": 0, "google_play": 1}
    chart_order = {"免费游戏榜": 0, "付费游戏榜": 1, "畅销榜": 2}

    sorted_keys = sorted(
        groups.keys(),
        key=lambda k: (store_order.get(k[0], 9), chart_order.get(k[1], 9), k[2])
    )

    for store, chart_name, region in sorted_keys:
        store_label = "App Store" if store == "appstore" else "Google Play"
        apps = sorted(groups[(store, chart_name, region)], key=lambda x: x.get("rank", 999))[:5]
        top5 = " / ".join([f"#{a['rank']} {a['name']}" for a in apps])
        lines.append(f"[{store_label}·{region}·{chart_name}] {top5}")

    return "\n".join(lines)


def analyze_changes(changes: list[dict], news_list: list = None) -> dict:
    """
    生成结构化的异动分析报告
    返回包含模块的字典：rising, falling, new_entries, regions, categories, industry
    """
    if not changes:
        return {
            "rising": [],
            "falling": [],
            "new_entries": [],
            "regions": "今日暂无显著榜单异动。",
            "categories": "今日暂无显著榜单异动。",
            "industry": ""
        }

    today = datetime.now().strftime("%Y年%m月%d日")
    news_text = ""
    if news_list:
        from scrapers.news_scraper import format_news_for_ai
        news_text = format_news_for_ai(news_list)

    # 整理异动数据
    change_lines = []
    for c in changes[:30]:
        region = c.get("region_name", "")
        store = "App Store" if c.get("store", "") != "google_play" else "Google Play"
        change_type = c["change_type"]
        name = c["name"]
        artist = c.get("artist", "")
        if change_type == "新进榜":
            change_lines.append(f"- {region}/{store}: 《{name}》({artist}) 新进榜 #{c['rank_today']}")
        elif change_type == "退榜":
            change_lines.append(f"- {region}/{store}: 《{name}》({artist}) 退榜（昨日#{c['rank_yesterday']}）")
        else:
            delta = abs(c.get("rank_delta", 0))
            change_lines.append(
                f"- {region}/{store}: 《{name}》({artist}) {change_type} {delta}位 "
                f"（#{c['rank_yesterday']}→#{c['rank_today']}）"
            )

    changes_text = "\n".join(change_lines)

    news_section = f"""
**最新行业新闻（供参考）：**
{news_text}
""" if news_text else ""

    prompt = f"""
请根据以下 {today} 手游榜单异动数据及行业新闻，生成结构化的异动分析。

**今日榜单异动：**
{changes_text}
{news_section}
---

请严格按照以下 JSON 格式输出，不要输出其他内容：

{{
  "rising": [
    {{
      "game": "游戏名",
      "change": "上升50位（#60→#10）",
      "region": "美国",
      "store": "App Store",
      "analysis": "简短分析原因，50字以内"
    }}
  ],
  "falling": [
    {{
      "game": "游戏名",
      "change": "下降30位（#5→#35）",
      "region": "美国",
      "store": "App Store",
      "analysis": "简短分析原因，50字以内"
    }}
  ],
  "new_entries": [
    {{
      "game": "游戏名",
      "change": "新进榜 #1",
      "region": "美国",
      "store": "App Store",
      "analysis": "简短分析原因，50字以内"
    }}
  ],
  "regions": "• 要点一：具体内容\\n\\n• 要点二：具体内容\\n\\n• 要点三：具体内容",
  "categories": "• 要点一：具体内容\\n\\n• 要点二：具体内容\\n\\n• 要点三：具体内容",
  "industry": "• 要点一：具体内容\\n\\n• 要点二：具体内容（如无相关新闻则为空字符串）"
}}

要求：
1. rising 数组：排名上升的游戏，选取 2-3 个最显著的
2. falling 数组：排名下降的游戏，选取 2-3 个最显著的
3. new_entries 数组：新进榜的游戏，选取 2-3 个最重要的
4. 每个 analysis 要简洁有力，点明关键原因
5. regions、categories、industry 必须分点陈述：
   - 每个要点以"•"开头
   - 每个要点之间用"\\n\\n"分隔（空一行）
   - 每个模块 2-3 个要点，每个要点不超过 30 字
6. regions 要提炼各地区的共性和差异
7. categories 要指出哪些品类在上升/下降
8. 只输出 JSON，不要有其他文字
"""

    system = "你是一位拥有10年经验的手游市场分析师。请基于数据和新闻给出专业、务实的分析。只输出合法的 JSON 格式，不要有任何其他文字。"
    
    result = call_minimax(prompt, system)
    
    # 解析 JSON 结果
    try:
        # 尝试提取 JSON（处理可能的 markdown 代码块）
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        parsed = json.loads(result.strip())
        return {
            "rising": parsed.get("rising", []),
            "falling": parsed.get("falling", []),
            "new_entries": parsed.get("new_entries", []),
            "regions": parsed.get("regions", ""),
            "categories": parsed.get("categories", ""),
            "industry": parsed.get("industry", "")
        }
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        # JSON 解析失败，返回原始文本作为 fallback
        print(f"[Warning] AI 返回非 JSON 格式，使用 fallback: {e}")
        return {
            "rising": [],
            "falling": [],
            "new_entries": [],
            "regions": result if result else "分析生成失败",
            "categories": "",
            "industry": "",
            "raw_text": result  # 保留原始文本供调试
        }


def analyze_changes_text(changes: list[dict], news_list: list = None) -> str:
    """
    生成纯文本格式的异动分析（用于 Excel 和企业微信）
    """
    analysis = analyze_changes(changes, news_list)
    
    lines = ["## 异动分析（对比昨日）\n"]
    
    # 上升
    if analysis.get("rising"):
        lines.append("### 📈 上升")
        for h in analysis["rising"]:
            lines.append(f"- **《{h.get('game', '')}》** {h.get('change', '')}（{h.get('region', '')} · {h.get('store', '')}）")
            lines.append(f"  {h.get('analysis', '')}")
        lines.append("")
    
    # 下降
    if analysis.get("falling"):
        lines.append("### 📉 下降")
        for h in analysis["falling"]:
            lines.append(f"- **《{h.get('game', '')}》** {h.get('change', '')}（{h.get('region', '')} · {h.get('store', '')}）")
            lines.append(f"  {h.get('analysis', '')}")
        lines.append("")
    
    # 新进榜
    if analysis.get("new_entries"):
        lines.append("### 🆕 新进榜")
        for h in analysis["new_entries"]:
            lines.append(f"- **《{h.get('game', '')}》** {h.get('change', '')}（{h.get('region', '')} · {h.get('store', '')}）")
            lines.append(f"  {h.get('analysis', '')}")
        lines.append("")
    
    # 地区趋势
    if analysis.get("regions"):
        lines.append("### 地区趋势")
        lines.append(analysis["regions"])
        lines.append("")
    
    # 品类动向
    if analysis.get("categories"):
        lines.append("### 品类动向")
        lines.append(analysis["categories"])
        lines.append("")
    
    # 行业动态
    if analysis.get("industry"):
        lines.append("### 行业动态")
        lines.append(analysis["industry"])
    
    # 如果有原始文本 fallback
    if analysis.get("raw_text") and not analysis.get("rising") and not analysis.get("falling") and not analysis.get("new_entries"):
        return analysis["raw_text"]
    
    return "\n".join(lines)


def generate_chart_summary_text(chart_data: list[dict], news_list: list = None) -> str:
    """
    生成第一部分：榜单概要
    直接基于数据生成，不调用 AI（节省 token）
    """
    today = datetime.now().strftime("%Y年%m月%d日")
    summary = build_chart_summary(chart_data)

    # 统计基本数字
    stores = set(a.get("store") for a in chart_data)
    regions = set(a.get("region_name") for a in chart_data)
    total = len(chart_data)

    header = f"""## 第一部分：{today} 榜单概要

**数据概览**
- 覆盖商店：{"App Store、Google Play" if len(stores) > 1 else list(stores)[0]}
- 覆盖地区：{len(regions)} 个（{"、".join(sorted(regions))}）
- 总记录数：{total} 条

**各地区 Top5 一览**
"""
    # 格式化为可读表格文本
    lines = []
    from collections import defaultdict
    groups = defaultdict(list)
    for app in chart_data:
        key = (app.get("store", ""), app.get("chart_name", ""), app.get("region_name", ""))
        groups[key].append(app)

    store_order = {"appstore": 0, "google_play": 1}
    chart_order = {"免费游戏榜": 0, "付费游戏榜": 1, "畅销榜": 2}
    sorted_keys = sorted(
        groups.keys(),
        key=lambda k: (store_order.get(k[0], 9), chart_order.get(k[1], 9), k[2])
    )

    current_store = ""
    current_chart = ""
    for store, chart_name, region in sorted_keys:
        store_label = "App Store" if store == "appstore" else "Google Play"
        if store_label != current_store or chart_name != current_chart:
            lines.append(f"\n**{store_label} · {chart_name}**")
            current_store = store_label
            current_chart = chart_name

        apps = sorted(groups[(store, chart_name, region)], key=lambda x: x.get("rank", 999))[:5]
        top5 = "、".join([f"#{a['rank']}{a['name']}" for a in apps])
        lines.append(f"- {region}：{top5}")

    return header + "\n".join(lines)


def generate_weekly_summary(all_week_changes: list[dict], top_charts: list[dict]) -> str:
    """生成周报摘要"""
    from collections import Counter
    app_counter = Counter(c["name"] for c in all_week_changes)
    top_movers = app_counter.most_common(10)
    movers_text = "\n".join([f"- 《{name}》: 出现 {count} 次异动" for name, count in top_movers])

    region_tops = defaultdict(list)
    for app in top_charts:
        if app.get("rank", 999) <= 3:
            region = app.get("region_name", "")
            region_tops[region].append(f"#{app['rank']} {app['name']}")

    region_text = "\n".join([f"**{r}**: {', '.join(tops)}" for r, tops in region_tops.items()])

    prompt = f"""
本周手游市场数据摘要：

**本周异动最频繁的游戏：**
{movers_text}

**各地区当前 Top3：**
{region_text}

请生成一份简洁的**周报**（约600字），包含：
1. **本周市场总结**（整体趋势，2-3段）
2. **重点关注产品**（3-5款值得持续跟踪的游戏及原因）
3. **下周预判**

语言：中文，Markdown 格式，适合发送给游戏公司产品/市场团队阅读。
"""
    system = "你是一位专业的手游市场周报分析师。"
    return call_minimax(prompt, system)
