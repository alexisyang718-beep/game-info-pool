"""
手游行业新闻抓取模块
抓取主流手游媒体 RSS，获取最近48小时内的新闻
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

NEWS_SOURCES = [
    {"name": "PocketGamer.biz",       "url": "https://www.pocketgamer.biz/rss/"},
    {"name": "GameDeveloper",          "url": "https://www.gamedeveloper.com/rss.xml"},
    {"name": "MobileGamer.biz",        "url": "https://mobilegamer.biz/feed/"},
    {"name": "Deconstructor of Fun",   "url": "https://www.deconstructoroffun.com/blog?format=rss"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GameInfoPool/1.0; +https://github.com)"
}


def _find_first(item, tags: list, ns: dict) -> object:
    """按优先级查找第一个存在的 XML 元素"""
    for tag in tags:
        el = item.find(tag, ns)
        if el is not None:
            return el
    return None


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def fetch_rss(source: dict, hours: int = 48) -> list[dict]:
    """抓取单个 RSS 源，返回最近 N 小时内的新闻"""
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//atom:entry", ns)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        news = []

        for item in items:
            # 标题
            title_el = _find_first(item, ["title", "atom:title"], ns)
            title = title_el.text.strip() if title_el is not None and title_el.text else ""

            # 链接
            link_el = _find_first(item, ["link", "atom:link"], ns)
            if link_el is not None:
                link = link_el.get("href") or (link_el.text or "")
            else:
                link = ""

            # 摘要
            desc_el = _find_first(item, ["description", "summary", "atom:summary", "content"], ns)
            description = ""
            if desc_el is not None and desc_el.text:
                description = _strip_html(desc_el.text)[:200]

            # 发布时间
            pub_el = _find_first(item, ["pubDate", "published", "atom:published", "dc:date"], ns)
            pub_date = None
            if pub_el is not None and pub_el.text:
                try:
                    pub_date = parsedate_to_datetime(pub_el.text.strip())
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                except Exception:
                    try:
                        pub_date = datetime.fromisoformat(
                            pub_el.text.strip().replace("Z", "+00:00")
                        )
                    except Exception:
                        pub_date = None

            if pub_date and pub_date < cutoff:
                continue

            if title:
                news.append({
                    "source": source["name"],
                    "title": title,
                    "link": link.strip(),
                    "description": description,
                    "pub_date": pub_date.isoformat() if pub_date else "",
                })

        return news

    except Exception as e:
        print(f"[News] 抓取失败 {source['name']}: {e}")
        return []


def fetch_all_news(hours: int = 48) -> list[dict]:
    """抓取所有新闻源，返回合并列表"""
    all_news = []
    for source in NEWS_SOURCES:
        print(f"[News] 抓取 {source['name']}...")
        items = fetch_rss(source, hours=hours)
        all_news.extend(items)
        print(f"  → {len(items)} 条")

    all_news.sort(key=lambda x: x.get("pub_date", ""), reverse=True)
    print(f"[News] 共获取 {len(all_news)} 条新闻")
    return all_news


def format_news_for_ai(news_list: list[dict], max_items: int = 15) -> str:
    """将新闻格式化为 AI 可读的文本"""
    if not news_list:
        return "（暂无最新行业新闻）"
    lines = []
    for item in news_list[:max_items]:
        lines.append(f"- 【{item['source']}】{item['title']}")
        if item.get("description"):
            lines.append(f"  摘要：{item['description']}")
    return "\n".join(lines)


if __name__ == "__main__":
    news = fetch_all_news()
    print("\n最新新闻：")
    for n in news[:5]:
        print(f"  [{n['source']}] {n['title']}")
