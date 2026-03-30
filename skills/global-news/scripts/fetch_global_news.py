#!/usr/bin/env python3
"""
Unified global news fetcher (self-contained).
Usage: python3 fetch_global_news.py [days_ago] [category] [--max-sources N]
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", "shared")))
from news_fetch_filters import apply_source_cap, item_in_date_window, parse_argv_max_sources, resolve_max_sources
from news_format import format_source_block

SUPPORTED_CATEGORIES = {
    "all",
    "domestic",
    "world",
    "economy",
    "geopolitics",
    "war",
    "politics",
    "tech",
    "security",
    "china",
}

CAT_NAMES = {
    "all": "📋 全部资讯",
    "domestic": "🇨🇳 国内动态",
    "world": "🌐 国际局势",
    "economy": "💹 经济财经",
    "geopolitics": "🌍 地缘政治",
    "war": "⚔️ 战争军事",
    "politics": "🏛️ 政治要闻",
    "tech": "📱 科技数码",
    "security": "🔐 安全资讯",
    "china": "🇨🇳 中国相关",
}

# Combined source list: china/media + world/mainstream
SOURCES: Dict[str, Dict[str, Any]] = {
    "xinhua_world": {"name": "新华网·国际", "kind": "rss", "url": "http://www.xinhuanet.com/world/news_world.xml", "icon": "🌐", "bucket": "china", "tags": ["all", "world", "geopolitics"]},
    "xinhua_politics": {"name": "新华网·时政", "kind": "rss", "url": "http://www.xinhuanet.com/politics/news_politics.xml", "icon": "🏛️", "bucket": "china", "tags": ["all", "domestic", "politics", "geopolitics"]},
    "xinhua_fortune": {"name": "新华网·财经", "kind": "rss", "url": "http://www.xinhuanet.com/fortune/news_fortune.xml", "icon": "💹", "bucket": "china", "tags": ["all", "economy", "domestic"]},
    "cns_scroll": {"name": "中新网·滚动", "kind": "rss", "url": "https://www.chinanews.com.cn/rss/scroll-news.xml", "icon": "📰", "bucket": "china", "tags": ["all", "domestic", "world", "economy", "geopolitics", "war", "politics"]},
    "bbc_cn": {"name": "BBC中文网", "kind": "rss", "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml", "icon": "🇬🇧", "bucket": "china", "tags": ["all", "world", "economy", "geopolitics", "war", "politics"]},
    "scmp_cn": {"name": "南华早报", "kind": "rss", "url": "https://www.scmp.com/rss/world.xml", "icon": "🇭🇰", "bucket": "china", "tags": ["all", "world", "economy", "geopolitics", "war"]},
    "sina_domestic": {"name": "新浪国内", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "2516", "num": "20", "page": "1"}, "icon": "🇨🇳", "bucket": "china", "tags": ["all", "domestic", "politics", "economy", "geopolitics"]},
    "sina_world": {"name": "新浪国际", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "2517", "num": "20", "page": "1"}, "icon": "🌐", "bucket": "china", "tags": ["all", "world", "geopolitics", "war"]},
    "sina_economy": {"name": "新浪财经", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "1686", "num": "20", "page": "1"}, "icon": "💹", "bucket": "china", "tags": ["all", "economy", "domestic"]},
    "sina_mil": {"name": "新浪军事", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "2425", "num": "20", "page": "1"}, "icon": "⚔️", "bucket": "china", "tags": ["all", "war", "geopolitics", "domestic"]},
    "sina_tech": {"name": "新浪科技", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "1195", "num": "20", "page": "1"}, "icon": "📱", "bucket": "china", "tags": ["all", "tech", "economy"]},
    "freebuf": {"name": "FreeBuf", "kind": "rss", "url": "https://www.freebuf.com/feed", "icon": "🔐", "bucket": "china", "tags": ["all", "tech", "security"]},
    "bbc_world": {"name": "BBC News", "kind": "rss", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "icon": "🇬🇧", "bucket": "world", "tags": ["all", "world", "china"]},
    "nytimes_world": {"name": "NY Times World", "kind": "rss", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "icon": "🇺🇸", "bucket": "world", "tags": ["all", "world", "china"]},
    "reuters_world": {"name": "Reuters", "kind": "rss", "url": "https://feeds.reuters.com/reuters/worldnews", "icon": "📰", "bucket": "world", "tags": ["all", "world"]},
    "bbc_business": {"name": "BBC Business", "kind": "rss", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "icon": "💷", "bucket": "world", "tags": ["all", "economy"]},
    "ft": {"name": "Financial Times", "kind": "rss", "url": "https://www.ft.com/rss/home", "icon": "💹", "bucket": "world", "tags": ["all", "economy"]},
    "theverge": {"name": "The Verge", "kind": "rss", "url": "https://www.theverge.com/rss/index.xml", "icon": "📱", "bucket": "world", "tags": ["all", "tech"]},
    "arstechnica": {"name": "Ars Technica", "kind": "rss", "url": "https://feeds.arstechnica.com/arstechnica/index", "icon": "🔧", "bucket": "world", "tags": ["all", "tech"]},
    "wired": {"name": "Wired", "kind": "rss", "url": "https://www.wired.com/feed/rss", "icon": "🔌", "bucket": "world", "tags": ["all", "tech"]},
}

FETCH_ORDER = [
    "xinhua_politics",
    "xinhua_fortune",
    "xinhua_world",
    "cns_scroll",
    "sina_domestic",
    "sina_world",
    "sina_economy",
    "sina_mil",
    "sina_tech",
    "bbc_cn",
    "scmp_cn",
    "freebuf",
    "bbc_world",
    "nytimes_world",
    "reuters_world",
    "bbc_business",
    "ft",
    "theverge",
    "arstechnica",
    "wired",
]


def parse_args(argv: List[str]) -> Tuple[int, str, Optional[int]]:
    days = 0
    category = "all"
    args, cli_cap = parse_argv_max_sources(argv)
    cap = resolve_max_sources(cli_cap)

    if len(args) > 0:
        if args[0].isdigit():
            days = int(args[0])
        else:
            category = args[0].lower()
    if len(args) > 1:
        if args[1].isdigit():
            days = int(args[1])
        else:
            category = args[1].lower()

    if category in {"intl", "international"}:
        category = "world"
    return days, category, cap


def _parse_pub_date(text: str) -> Optional[datetime]:
    s = (text or "").strip()
    if not s:
        return None
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%a, %d %b %Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:25], fmt)
        except Exception:
            pass
    return None


def fetch_rss(config: Dict[str, Any], days: int) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(str(config["url"]), headers={"User-Agent": "Mozilla/5.0", "Accept": "application/rss+xml, application/xml, text/xml, */*"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            m = re.search(r"<rss[^>]*>.*?</rss>", content, re.DOTALL)
            if not m:
                return {"name": config["name"], "icon": config["icon"], "results": [], "count": 0, "error": "解析失败"}
            root = ET.fromstring(m.group(0))
        items = root.findall(".//item") or root.findall(".//entry") or []
        out = []
        for item in items:
            title = (item.findtext("title") or "").strip()
            if not title:
                continue
            link = (item.findtext("link") or item.findtext("guid") or "").strip()
            desc = (item.findtext("description") or item.findtext("summary") or item.findtext("content") or item.findtext("content:encoded") or "").strip()
            desc = re.sub(r"<[^>]+>", "", html.unescape(desc))[:200]
            pub_date = _parse_pub_date(item.findtext("pubDate") or item.findtext("published") or item.findtext("updated") or item.findtext("dc:date") or "")
            if not item_in_date_window(pub_date, days):
                continue
            out.append({"title": title, "link": link.split("?")[0], "date": pub_date, "description": desc})
        return {"name": config["name"], "icon": config["icon"], "results": out, "count": len(out)}
    except urllib.error.HTTPError as e:
        return {"name": config["name"], "icon": config["icon"], "results": [], "count": 0, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"name": config["name"], "icon": config["icon"], "results": [], "count": 0, "error": str(e)}


def fetch_sina(config: Dict[str, Any], days: int) -> Dict[str, Any]:
    try:
        params = config["params"]
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{config['api_url']}?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://news.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = []
        for item in data.get("result", {}).get("data", []):
            title = (item.get("title") or "").strip()
            if not title:
                continue
            pub_date = None
            ctime = item.get("ctime")
            if ctime:
                try:
                    pub_date = datetime.fromtimestamp(int(ctime))
                except Exception:
                    pub_date = None
            if not item_in_date_window(pub_date, days):
                continue
            out.append({"title": title, "link": (item.get("url") or "").split("?")[0], "date": pub_date, "description": ""})
        return {"name": config["name"], "icon": config["icon"], "results": out, "count": len(out)}
    except Exception as e:
        return {"name": config["name"], "icon": config["icon"], "results": [], "count": 0, "error": str(e)}


def source_matches(config: Dict[str, Any], category: str) -> bool:
    tags = set(config.get("tags", []))
    return category == "all" or category in tags


def should_show_world_bucket(category: str) -> bool:
    return category in {"all", "world", "economy", "tech", "china"}


def format_section(title: str, rows: List[Tuple[str, Dict[str, Any]]]) -> str:
    blocks: List[str] = [title, ""]
    for _, result in rows:
        if result.get("count", 0) == 0:
            continue
        if "error" in result:
            blocks.append(f"{result['icon']} **{result['name']}** · ❌ {result['error']}")
            blocks.append("")
            continue
        items = result["results"]
        blocks.extend(format_source_block(result["icon"], f"{result['name']}（{len(items)} 条）", items, max_items=6, desc_max=160))
        blocks.append("")
    return "\n".join(blocks).rstrip()


def main() -> None:
    days, category, cap = parse_args(sys.argv[1:])
    if category not in SUPPORTED_CATEGORIES:
        print(f"Unsupported category: {category}")
        print("Supported:", ", ".join(sorted(SUPPORTED_CATEGORIES)))
        sys.exit(2)

    selected = [sid for sid in FETCH_ORDER if sid in SOURCES and source_matches(SOURCES[sid], category)]
    selected = apply_source_cap(selected, cap)

    results: Dict[str, Dict[str, Any]] = {}
    for sid in selected:
        cfg = SOURCES[sid]
        if cfg["kind"] == "sina":
            results[sid] = fetch_sina(cfg, days)
        else:
            results[sid] = fetch_rss(cfg, days)

    china_rows = [(sid, results[sid]) for sid in selected if SOURCES[sid]["bucket"] == "china" and results.get(sid)]
    world_rows = [(sid, results[sid]) for sid in selected if SOURCES[sid]["bucket"] == "world" and results.get(sid)]

    pieces: List[str] = [f"{CAT_NAMES.get(category, '📋 全部资讯')} {datetime.now().strftime('%m-%d')}"]
    china_body = format_section("## 🇨🇳 国内与中文源", china_rows) if china_rows else ""
    world_body = format_section("## 🌍 国际主流源", world_rows) if world_rows and should_show_world_bucket(category) else ""
    if china_body:
        pieces.append(china_body)
    if world_body:
        pieces.append(world_body)

    out = "\n\n".join([p for p in pieces if p]).strip()
    if not out:
        out = "📭 暂无相关资讯"
    if cap is not None:
        out = f"（本 run 抓取 {len(selected)} 个源，上限 {cap}）\n\n" + out
    print(out)


if __name__ == "__main__":
    main()
