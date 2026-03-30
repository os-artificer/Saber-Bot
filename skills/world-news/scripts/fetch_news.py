#!/usr/bin/env python3
"""
Fetch major world news from multiple authoritative sources.
Usage: python3 fetch_news.py [days_ago] [category]
    days_ago: number of days to look back (default: 0 = today only)
    category: all, world, economy, tech, china (default: all)
"""

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.request
import urllib.error
import html
import re

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "..", "shared")))
from news_fetch_filters import (
    apply_source_cap,
    item_in_date_window,
    parse_argv_max_sources,
    resolve_max_sources,
)
from news_format import format_source_block

# Source configurations
BBC_WORLD = {
    "name": "BBC News",
    "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "lang": "en",
    "icon": "🇬🇧",
}
BBC_BUSINESS = {
    "name": "BBC Business",
    "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "lang": "en",
    "icon": "💷",
}
NYT_WORLD = {
    "name": "NY Times World",
    "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "lang": "en",
    "icon": "🇺🇸",
}
NYT_BUSINESS = {
    "name": "NY Times Business",
    "url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "lang": "en",
    "icon": "📊",
}
FT = {
    "name": "Financial Times",
    "url": "https://www.ft.com/rss/home",
    "lang": "en",
    "icon": "💹",
}
SCMP = {
    "name": "SCMP",
    "url": "https://www.scmp.com/rss/world.xml",
    "lang": "en",
    "icon": "🇭🇰",
}
REUTERS = {
    "name": "Reuters",
    "url": "https://feeds.reuters.com/reuters/worldnews",
    "lang": "en",
    "icon": "📰",
}
VERGE = {
    "name": "The Verge",
    "url": "https://www.theverge.com/rss/index.xml",
    "lang": "en",
    "icon": "📱",
}
ARS = {
    "name": "Ars Technica",
    "url": "https://feeds.arstechnica.com/arstechnica/index",
    "lang": "en",
    "icon": "🔧",
}
TCRUNCH = {
    "name": "TechCrunch",
    "url": "https://techcrunch.com/feed/",
    "lang": "en",
    "icon": "💰",
}
WIRED = {
    "name": "Wired",
    "url": "https://www.wired.com/feed/rss",
    "lang": "en",
    "icon": "🔌",
}
TNS = {
    "name": "The New Stack",
    "url": "https://thenewstack.io/feed/",
    "lang": "en",
    "icon": "☁️",
}
GUARDIAN_WORLD = {
    "name": "The Guardian World",
    "url": "https://www.theguardian.com/world/rss",
    "lang": "en",
    "icon": "🛡️",
}
ALJAZEERA = {
    "name": "Al Jazeera English",
    "url": "https://www.aljazeera.com/xml/rss/all.xml",
    "lang": "en",
    "icon": "🕌",
}
NPR_NEWS = {
    "name": "NPR News",
    "url": "https://feeds.npr.org/1001/rss.xml",
    "lang": "en",
    "icon": "📻",
}
INDEPENDENT_WORLD = {
    "name": "The Independent World",
    "url": "https://www.independent.co.uk/news/world/rss",
    "lang": "en",
    "icon": "📰",
}
FRANCE24 = {
    "name": "France 24",
    "url": "https://www.france24.com/en/rss",
    "lang": "en",
    "icon": "🇫🇷",
}
SKY_WORLD = {
    "name": "Sky News World",
    "url": "https://feeds.skynews.com/feeds/rss/world.xml",
    "lang": "en",
    "icon": "📡",
}
ECONOMIST_WEEK = {
    "name": "The Economist World This Week",
    "url": "https://www.economist.com/the-world-this-week/rss.xml",
    "lang": "en",
    "icon": "📰",
}

# Category to sources mapping
SOURCES = {
    "all": {
        "bbc_world": BBC_WORLD,
        "bbc_business": BBC_BUSINESS,
        "nytimes_world": NYT_WORLD,
        "nytimes_business": NYT_BUSINESS,
        "ft": FT,
        "scmp": SCMP,
        "reuters": REUTERS,
        "guardian_world": GUARDIAN_WORLD,
        "aljazeera": ALJAZEERA,
        "npr_news": NPR_NEWS,
        "independent_world": INDEPENDENT_WORLD,
        "france24": FRANCE24,
        "sky_world": SKY_WORLD,
        "economist_week": ECONOMIST_WEEK,
        "theverge": VERGE,
        "arstechnica": ARS,
        "wired": WIRED,
        "tns": TNS,
        "techcrunch": TCRUNCH,
    },
    "world": {
        "bbc_world": BBC_WORLD,
        "nytimes_world": NYT_WORLD,
        "scmp": SCMP,
        "reuters": REUTERS,
        "guardian_world": GUARDIAN_WORLD,
        "aljazeera": ALJAZEERA,
        "npr_news": NPR_NEWS,
        "independent_world": INDEPENDENT_WORLD,
        "france24": FRANCE24,
        "sky_world": SKY_WORLD,
    },
    "economy": {
        "bbc_business": BBC_BUSINESS,
        "nytimes_business": NYT_BUSINESS,
        "ft": FT,
        "economist_week": ECONOMIST_WEEK,
        "techcrunch": TCRUNCH,
    },
    "tech": {
        "theverge": VERGE,
        "arstechnica": ARS,
        "wired": WIRED,
        "tns": TNS,
        "techcrunch": TCRUNCH,
    },
    "china": {
        "scmp": SCMP,
        "nytimes_world": NYT_WORLD,
        "bbc_world": BBC_WORLD,
    }
}

# 抓取与展示顺序（用于 --max-sources / OPENCLAW_NEWS_MAX_SOURCES）
WORLD_NEWS_SOURCE_ORDER = [
    "bbc_world",
    "bbc_business",
    "nytimes_world",
    "nytimes_business",
    "ft",
    "scmp",
    "reuters",
    "guardian_world",
    "aljazeera",
    "npr_news",
    "independent_world",
    "france24",
    "sky_world",
    "economist_week",
    "theverge",
    "arstechnica",
    "wired",
    "tns",
    "techcrunch",
]

def fetch_source(source_id, config, days_ago=0):
    """Fetch news from a single source."""
    try:
        req = urllib.request.Request(config["url"], headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode('utf-8')
        
        root = ET.fromstring(content)
        items = root.findall('.//item') or root.findall('.//entry') or []
        
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
                item.findtext('dc:date') or
                ''
            ).strip()
            
            description = (
                item.findtext('description') or 
                item.findtext('summary') or 
                item.findtext('content') or
                item.findtext('content:encoded') or 
                ''
            ).strip()
            description = html.unescape(description) if description else ''
            description = re.sub(r'<[^>]+>', '', description)
            description = description[:300] + '...' if len(description) > 300 else description
            
            # Parse date
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

def format_output(source_results, category="all"):
    """Format all results into readable output."""
    output = []
    total = 0
    cat_names = {"all": "全部", "world": "国际", "economy": "经济", "tech": "科技", "china": "中国相关"}
    
    order = WORLD_NEWS_SOURCE_ORDER
    
    output.append(f"🌍 **世界资讯速览**（{cat_names.get(category, '全部')}）")
    output.append("")
    
    for source_id in order:
        if source_id not in source_results:
            continue
        result = source_results[source_id]
        if not result or result["count"] == 0:
            continue
        
        icon = result["icon"]
        name = result["name"]
        items = result["results"]
        
        if "error" in result:
            output.append(f"{icon} **{name}** · ❌ {result['error']}")
            output.append("")
            continue
        
        total += len(items)
        output.extend(
            format_source_block(
                icon, f"{name}（{len(items)} 条）", items, max_items=6, desc_max=160
            )
        )
        output.append("")
    
    if total == 0:
        return "今日无相关资讯。"
    
    return "\n".join(output).rstrip()

if __name__ == "__main__":
    days = 0
    category = "all"
    argv, cli_cap = parse_argv_max_sources(sys.argv[1:])
    max_cap = resolve_max_sources(cli_cap)
    
    if len(argv) > 0:
        if argv[0].isdigit():
            days = int(argv[0])
    
    if len(argv) > 1:
        category = argv[1].lower()
    
    sources_full = SOURCES.get(category, SOURCES["all"])
    order_keys = [k for k in WORLD_NEWS_SOURCE_ORDER if k in sources_full]
    order_keys = apply_source_cap(order_keys, max_cap)
    sources = {k: sources_full[k] for k in order_keys}
    
    results = {}
    for source_id, config in sources.items():
        results[source_id] = fetch_source(source_id, config, days)
    
    out = format_output(results, category)
    if max_cap is not None:
        out = f"（本 run 抓取 {len(sources)} 个源，上限 {max_cap}）\n\n" + out
    print(out)
