#!/usr/bin/env python3
"""
Fetch China-focused news from multiple sources.
国内以政务与权威央媒 RSS（新华网、人民网、中新网）为主，辅以新浪 API 与科技媒体；
国际中文媒体：BBC、纽时、南华早报、路透社等。

Usage: python3 fetch_china_news.py [days_ago] [category]
    days_ago: number of days to look back (default: 0 = today only)
    category: all | domestic | world | economy | geopolitics | war | politics (default: all)
"""

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.request
import urllib.error
import html
import re
import json

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", "shared")))
from news_fetch_filters import (
    apply_source_cap,
    item_in_date_window,
    parse_argv_max_sources,
    resolve_max_sources,
)
from news_format import format_source_block

# ============================================================
# RSS Sources
# ============================================================

# 政务与权威央媒（新华社、人民日报、中国新闻网等 — 优先展示）
STATE_MEDIA_SOURCES = {
    "xinhua_politics": {
        "name": "新华网·时政",
        "url": "http://www.xinhuanet.com/politics/news_politics.xml",
        "icon": "🏛️",
        "tags": ["all", "domestic", "politics", "geopolitics"],
    },
    "xinhua_fortune": {
        "name": "新华网·财经",
        "url": "http://www.xinhuanet.com/fortune/news_fortune.xml",
        "icon": "💹",
        "tags": ["all", "economy", "domestic"],
    },
    "xinhua_world": {
        "name": "新华网·国际",
        "url": "http://www.xinhuanet.com/world/news_world.xml",
        "icon": "🌐",
        "tags": ["all", "world", "geopolitics"],
    },
    "xinhua_mil": {
        "name": "新华网·军事",
        "url": "http://www.xinhuanet.com/mil/news_mil.xml",
        "icon": "⚔️",
        "tags": ["all", "war", "geopolitics", "domestic"],
    },
    "xinhua_legal": {
        "name": "新华网·法治",
        "url": "http://www.xinhuanet.com/legal/news_legal.xml",
        "icon": "⚖️",
        "tags": ["all", "politics", "domestic"],
    },
    "xinhua_tech": {
        "name": "新华网·科技",
        "url": "http://www.xinhuanet.com/tech/news_tech.xml",
        "icon": "🔬",
        "tags": ["all", "tech", "domestic", "economy"],
    },
    "xinhua_energy": {
        "name": "新华网·能源",
        "url": "http://www.xinhuanet.com/energy/news_energy.xml",
        "icon": "⚡",
        "tags": ["all", "economy", "domestic"],
    },
    "people_politics": {
        "name": "人民网·时政",
        "url": "http://www.people.com.cn/rss/politics.xml",
        "icon": "🇨🇳",
        "tags": ["all", "domestic", "politics", "geopolitics"],
    },
    "people_finance": {
        "name": "人民网·财经",
        "url": "http://www.people.com.cn/rss/finance.xml",
        "icon": "💹",
        "tags": ["all", "economy", "domestic"],
    },
    "people_society": {
        "name": "人民网·社会",
        "url": "http://www.people.com.cn/rss/society.xml",
        "icon": "👥",
        "tags": ["all", "domestic", "politics"],
    },
    "people_world": {
        "name": "人民网·国际",
        "url": "http://www.people.com.cn/rss/world.xml",
        "icon": "🌍",
        "tags": ["all", "world", "geopolitics"],
    },
    "cns_scroll": {
        "name": "中新网·滚动",
        "url": "https://www.chinanews.com.cn/rss/scroll-news.xml",
        "icon": "📰",
        "tags": ["all", "domestic", "politics", "economy", "world", "geopolitics", "war"],
    },
    "cns_finance": {
        "name": "中新网·财经",
        "url": "https://www.chinanews.com.cn/rss/finance.xml",
        "icon": "💹",
        "tags": ["all", "economy", "domestic"],
    },
    "cns_world": {
        "name": "中新网·国际",
        "url": "https://www.chinanews.com.cn/rss/world.xml",
        "icon": "🌏",
        "tags": ["all", "world", "geopolitics"],
    },
    "cns_mil": {
        "name": "中新网·军事",
        "url": "https://www.chinanews.com.cn/rss/mil.xml",
        "icon": "⚔️",
        "tags": ["all", "war", "geopolitics", "domestic"],
    },
    "cns_it": {
        "name": "中新网·IT",
        "url": "https://www.chinanews.com.cn/rss/it.xml",
        "icon": "💻",
        "tags": ["all", "tech", "domestic"],
    },
}

STATE_MEDIA_ORDER = [
    "xinhua_politics",
    "xinhua_fortune",
    "xinhua_world",
    "xinhua_mil",
    "xinhua_legal",
    "xinhua_tech",
    "xinhua_energy",
    "people_politics",
    "people_finance",
    "people_society",
    "people_world",
    "cns_scroll",
    "cns_finance",
    "cns_world",
    "cns_mil",
    "cns_it",
]

# 国际中文媒体
INTL_CHINESE_SOURCES = {
    "bbc_cn": {
        "name": "BBC中文网",
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "icon": "🇬🇧",
        "tags": ["all", "world", "economy", "geopolitics", "war", "politics"]
    },
    "nyt_cn": {
        "name": "纽约时报中文",
        "url": "https://cn.nytimes.com/rss.html",
        "icon": "🇺🇸",
        "tags": ["all", "politics", "economy", "geopolitics", "world"]
    },
    "scmp": {
        "name": "南华早报",
        "url": "https://www.scmp.com/rss/world.xml",
        "icon": "🇭🇰",
        "tags": ["all", "world", "geopolitics", "economy", "war"]
    },
    "reuters_cn": {
        "name": "路透社中文",
        "url": "https://www.reutersagency.com/feed/?best-topics=china&post_type=best&lang=zh",
        "icon": "📰",
        "tags": ["all", "economy", "politics", "geopolitics", "world"]
    },
}

# 科技媒体 RSS
TECH_SOURCES = {
    "36kr": {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "icon": "📱",
        "tags": ["all", "economy", "tech", "domestic"]
    },
    "tmtpost": {
        "name": "钛媒体",
        "url": "https://www.tmtpost.com/rss",
        "icon": "🔩",
        "tags": ["all", "tech", "economy", "domestic"]
    },
    "ifanr": {
        "name": "爱范儿",
        "url": "https://www.ifanr.com/rss",
        "icon": "📲",
        "tags": ["all", "tech", "domestic"]
    },
    "appinn": {
        "name": "小众软件",
        "url": "https://www.appinn.com/feed",
        "icon": "🔧",
        "tags": ["all", "tech", "domestic"]
    },
    "freebuf": {
        "name": "FreeBuf",
        "url": "https://www.freebuf.com/feed",
        "icon": "🔐",
        "tags": ["all", "tech", "security", "domestic"]
    },
}

# Merge all RSS sources（政务央媒优先合并顺序）
RSS_SOURCES = {}
RSS_SOURCES.update(STATE_MEDIA_SOURCES)
RSS_SOURCES.update(INTL_CHINESE_SOURCES)
RSS_SOURCES.update(TECH_SOURCES)

SINA_SOURCE_ORDER = ["sina_domestic", "sina_world", "sina_economy", "sina_mil", "sinaTech"]
TECH_SOURCE_ORDER = ["36kr", "tmtpost", "ifanr", "appinn", "freebuf"]
INTL_SOURCE_ORDER = ["bbc_cn", "nyt_cn", "scmp", "reuters_cn"]

# ============================================================
# Sina API Sources (domestic China news)
# ============================================================

SINA_SECTIONS = {
    "sina_domestic": {
        "name": "新浪国内",
        "api_url": "https://feed.mix.sina.com.cn/api/roll/get",
        "params": {"pageid": "153", "lid": "2516", "num": "20", "page": "1"},
        "icon": "🇨🇳",
        "tags": ["all", "domestic", "politics", "economy", "geopolitics"]
    },
    "sina_world": {
        "name": "新浪国际",
        "api_url": "https://feed.mix.sina.com.cn/api/roll/get",
        "params": {"pageid": "153", "lid": "2517", "num": "20", "page": "1"},
        "icon": "🌐",
        "tags": ["all", "world", "geopolitics", "war"]
    },
    "sina_economy": {
        "name": "新浪财经",
        "api_url": "https://feed.mix.sina.com.cn/api/roll/get",
        "params": {"pageid": "153", "lid": "1686", "num": "20", "page": "1"},
        "icon": "💹",
        "tags": ["all", "economy", "domestic"]
    },
    "sina_mil": {
        "name": "新浪军事",
        "api_url": "https://feed.mix.sina.com.cn/api/roll/get",
        "params": {"pageid": "153", "lid": "2425", "num": "20", "page": "1"},
        "icon": "⚔️",
        "tags": ["all", "war", "geopolitics", "domestic"]
    },
    "sinaTech": {
        "name": "新浪科技",
        "api_url": "https://feed.mix.sina.com.cn/api/roll/get",
        "params": {"pageid": "153", "lid": "1195", "num": "20", "page": "1"},
        "icon": "📱",
        "tags": ["all", "economy", "tech"]
    },
}


def _build_china_fetch_order() -> list:
    """抓取顺序：政务央媒 → 新浪 → 科技 → 国际；再补全其余 RSS/新浪键。"""
    seen: set[str] = set()
    out: list[str] = []
    for block in (
        STATE_MEDIA_ORDER,
        SINA_SOURCE_ORDER,
        TECH_SOURCE_ORDER,
        INTL_SOURCE_ORDER,
        list(RSS_SOURCES.keys()),
        list(SINA_SECTIONS.keys()),
    ):
        for sid in block:
            if sid not in seen:
                seen.add(sid)
                out.append(sid)
    return out


CHINA_FETCH_ORDER = _build_china_fetch_order()

# ============================================================
# Category configurations
# ============================================================

CATEGORIES = {
    "all":        {"name": "📋 全部资讯", "icon": "📋"},
    "domestic":   {"name": "🇨🇳 国内动态", "icon": "🇨🇳"},
    "world":      {"name": "🌐 国际局势", "icon": "🌐"},
    "economy":    {"name": "💹 经济财经", "icon": "💹"},
    "geopolitics":{"name": "🌍 地缘政治", "icon": "🌍"},
    "war":        {"name": "⚔️ 战争军事", "icon": "⚔️"},
    "politics":   {"name": "🏛️ 政治要闻", "icon": "🏛️"},
    "tech":       {"name": "📱 科技数码", "icon": "📱"},
    "security":   {"name": "🔐 安全资讯", "icon": "🔐"},
}

# ============================================================
# Fetch functions
# ============================================================

def fetch_rss_source(source_id, config, days_ago=0):
    """Fetch news from an RSS source."""
    try:
        req = urllib.request.Request(config["url"], headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            match = re.search(r'<rss[^>]*>.*?</rss>', content, re.DOTALL)
            if match:
                root = ET.fromstring(match.group(0))
            else:
                return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": "解析失败", "results": [], "count": 0}
        
        items = root.findall('.//item') or root.findall('.//entry') or []
        if not items:
            channel = root.find('.//channel')
            if channel is not None:
                items = channel.findall('.//item') or channel.findall('.//entry') or []
        
        results = []
        
        for item in items:
            title = (item.findtext('title') or '').strip()
            if not title:
                continue
            
            link = (item.findtext('link') or '').strip()
            if not link:
                link = (item.findtext('guid') or '').strip()
            
            pub_date_str = (
                item.findtext('pubDate') or 
                item.findtext('published') or 
                item.findtext('updated') or 
                item.findtext('dc:date') or ''
            ).strip()
            
            description = (
                item.findtext('description') or 
                item.findtext('summary') or 
                item.findtext('content') or ''
            ).strip()
            description = html.unescape(description) if description else ''
            description = re.sub(r'<[^>]+>', '', description)
            description = description[:200] + '…' if len(description) > 200 else description
            
            pub_date = None
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %Z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S%z',
                '%a, %d %b %Y %H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
            ]
            for fmt in date_formats:
                try:
                    pub_date = datetime.strptime(pub_date_str[:25], fmt)
                    break
                except Exception:
                    pass
            
            if not item_in_date_window(pub_date, days_ago):
                continue
            
            if title:
                results.append({
                    'title': title,
                    'link': link.split('?')[0] if link else '',
                    'date': pub_date,
                    'description': description,
                    'source': source_id
                })
        
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "results": results, "count": len(results)}
        
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}


def fetch_sina_source(source_id, config, days_ago=0):
    """Fetch news from Sina API."""
    try:
        params = config["params"]
        params_encoded = '&'.join([f"{k}={v}" for k, v in params.items()])
        url = f"{config['api_url']}?{params_encoded}"
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://news.sina.com.cn',
        })
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        items = data.get('result', {}).get('data', [])
        results = []
        
        for item in items:
            title = (item.get('title') or '').strip()
            if not title:
                continue
            
            link = (item.get('url') or '').strip()
            
            # Parse ctime (Unix timestamp)
            ctime = item.get('ctime', '')
            pub_date = None
            if ctime:
                try:
                    pub_date = datetime.fromtimestamp(int(ctime))
                except Exception:
                    pass
            
            if not item_in_date_window(pub_date, days_ago):
                continue
            
            if title:
                results.append({
                    'title': title,
                    'link': link.split('?')[0] if link else '',
                    'date': pub_date,
                    'description': '',
                    'source': source_id
                })
        
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "results": results, "count": len(results)}
        
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}


# ============================================================
# Formatting
# ============================================================

def format_output(source_results, category="all"):
    """Format all results into readable plain text output."""
    today = datetime.now().strftime('%m-%d')
    cat_info = CATEGORIES.get(category, CATEGORIES["all"])
    
    # Define display order
    state_order = STATE_MEDIA_ORDER
    domestic_order = SINA_SOURCE_ORDER
    intl_order = INTL_SOURCE_ORDER
    tech_order = TECH_SOURCE_ORDER
    
    # Check if a source matches category filter
    def matches_category(source_id, config):
        tags = config.get("tags", [])
        if category == "all":
            return True
        if category in tags:
            return True
        return False
    
    # Filter 政务央媒 RSS
    state_filtered = [
        sid
        for sid in state_order
        if sid in source_results and matches_category(sid, STATE_MEDIA_SOURCES.get(sid, {}))
    ]

    # Filter domestic sources（新浪 API）
    dom_order = [sid for sid in domestic_order 
                 if sid in source_results 
                 and matches_category(sid, SINA_SECTIONS.get(sid, {}))]
    
    # Filter international sources
    intl_filtered = [sid for sid in intl_order 
                     if sid in source_results 
                     and matches_category(sid, INTL_CHINESE_SOURCES.get(sid, {}))]
    
    # Filter tech sources
    tech_filtered = [sid for sid in tech_order 
                     if sid in source_results 
                     and matches_category(sid, TECH_SOURCES.get(sid, {}))]
    
    total = sum(r["count"] for r in source_results.values() if "count" in r)
    
    output = []
    output.append(f"{cat_info['name']} {today} · 共 {total} 条")
    output.append("")
    
    # 政务与权威央媒（新华 / 人民 / 中新网 RSS）
    has_state = any(source_results.get(sid, {}).get("count", 0) > 0 for sid in state_filtered)
    if has_state:
        output.append("### 🏛️ 政务与权威央媒（新华 / 人民 / 中新网）")
        output.append("")
        for sid in state_order:
            if sid not in state_filtered:
                continue
            result = source_results.get(sid)
            if not result or result.get("count", 0) == 0:
                continue
            if "error" in result:
                output.append(f"{result['icon']} **{result['name']}** · ❌ {result['error']}")
                output.append("")
                continue
            n = len(result["results"])
            output.extend(
                format_source_block(
                    result["icon"],
                    f"{result['name']}（{n} 条）",
                    result["results"],
                    max_items=5,
                    desc_max=160,
                )
            )
            output.append("")
    
    # 新浪 API（商业门户聚合）
    has_domestic = any(source_results.get(sid, {}).get("count", 0) > 0 for sid in dom_order)
    if has_domestic:
        output.append("### 📰 全国性门户（新浪 API）")
        output.append("")
        for sid in domestic_order:
            if sid not in dom_order:
                continue
            result = source_results.get(sid)
            if not result or result.get("count", 0) == 0:
                continue
            if "error" in result:
                output.append(f"{result['icon']} **{result['name']}** · ❌ {result['error']}")
                output.append("")
                continue
            n = len(result["results"])
            output.extend(
                format_source_block(
                    result["icon"],
                    f"{result['name']}（{n} 条）",
                    result["results"],
                    max_items=5,
                    desc_max=160,
                )
            )
            output.append("")
    
    # Tech section
    has_tech = any(source_results.get(sid, {}).get("count", 0) > 0 for sid in tech_filtered)
    if has_tech and (category == "all" or category in ["tech", "security"]):
        output.append("### 📱 科技数码")
        output.append("")
        for sid in tech_order:
            if sid not in tech_filtered:
                continue
            result = source_results.get(sid)
            if not result or result.get("count", 0) == 0:
                continue
            if "error" in result:
                output.append(f"{result['icon']} **{result['name']}** · ❌ {result['error']}")
                output.append("")
                continue
            n = len(result["results"])
            output.extend(
                format_source_block(
                    result["icon"],
                    f"{result['name']}（{n} 条）",
                    result["results"],
                    max_items=5,
                    desc_max=160,
                )
            )
            output.append("")
    
    # International Chinese-language media
    has_intl = any(source_results.get(sid, {}).get("count", 0) > 0 for sid in intl_filtered)
    if has_intl:
        output.append("### 🌍 国际中文媒体")
        output.append("")
        for sid in intl_order:
            if sid not in intl_filtered:
                continue
            result = source_results.get(sid)
            if not result or result.get("count", 0) == 0:
                continue
            if "error" in result:
                output.append(f"{result['icon']} **{result['name']}** · ❌ {result['error']}")
                output.append("")
                continue
            n = len(result["results"])
            output.extend(
                format_source_block(
                    result["icon"],
                    f"{result['name']}（{n} 条）",
                    result["results"],
                    max_items=5,
                    desc_max=160,
                )
            )
            output.append("")
    
    if total == 0:
        return "📭 暂无相关资讯"
    
    return '\n'.join(output)


def main():
    days = 0
    category = "all"
    argv, cli_cap = parse_argv_max_sources(sys.argv[1:])
    max_cap = resolve_max_sources(cli_cap)
    
    if len(argv) > 0:
        if argv[0].isdigit():
            days = int(argv[0])
        elif argv[0] in CATEGORIES:
            category = argv[0]
    
    if len(argv) > 1:
        if argv[1].isdigit():
            days = int(argv[1])
        elif argv[1] in CATEGORIES:
            category = argv[1]
    
    fetch_ids = apply_source_cap(CHINA_FETCH_ORDER, max_cap)
    results = {}
    for source_id in fetch_ids:
        if source_id in RSS_SOURCES:
            results[source_id] = fetch_rss_source(source_id, RSS_SOURCES[source_id], days)
        elif source_id in SINA_SECTIONS:
            results[source_id] = fetch_sina_source(source_id, SINA_SECTIONS[source_id], days)
    
    out = format_output(results, category)
    if max_cap is not None:
        out = f"（本 run 抓取 {len(fetch_ids)} 个源，上限 {max_cap}）\n\n" + out
    print(out)


if __name__ == "__main__":
    main()
