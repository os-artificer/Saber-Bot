#!/usr/bin/env python3
"""
Fetch AI/Tech news from multiple authoritative IT news sources.
入口: python3 fetch_ai_news.py（跨平台，不依赖 Bash）。
Usage: python3 fetch_ai_news.py [days_ago] [site_filter]
    days_ago: number of days to look back (default: 3 ≈ past 72 hours rolling)
    site_filter: comma-separated list of site codes (e.g., "en,cn,verge")
                 or "all" for everything (default: "en,cn")
    
Site codes:
    en     - InfoQ English (infoq.com)
    cn     - InfoQ 中文 (infoq.cn)
    verge  - The Verge
    ars    - Ars Technica
    tc     - TechCrunch
    wired  - Wired
    hn     - Hacker News
    tns    - The New Stack
    vb     - VentureBeat
    devto  - dev.to
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
    DEFAULT_NEWS_LOOKBACK_DAYS,
    apply_source_cap,
    item_in_date_window,
    parse_argv_max_sources,
    resolve_max_sources,
)
from news_format import collect_urls_from_results, format_source_block, format_url_appendix_block
from rss_links import extract_item_link
from tech_rss_ai_sources import AI_NEWS_SOURCE_ORDER, AI_REGION_ORDER, SOURCES

def is_ai_related(title, description, keywords):
    """Check if content is AI-related based on keywords."""
    text = f"{title} {description}".lower()
    return any(kw.lower() in text for kw in keywords)

def _atom_ns(tag: str) -> str:
    return f"{{http://www.w3.org/2005/Atom}}{tag}"

def fetch_source(source_id, config, days_ago=None):
    """Fetch and filter news from a single source."""
    if days_ago is None:
        days_ago = DEFAULT_NEWS_LOOKBACK_DAYS
    try:
        req = urllib.request.Request(config["url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode('utf-8')
        
        root = ET.fromstring(content)
        items = root.findall('.//item') or root.findall('.//entry') or []
        
        results = []
        
        for item in items:
            title = (
                (item.findtext('title') or '').strip()
                or (item.findtext(_atom_ns('title')) or '').strip()
            )
            desc_raw = (
                (item.findtext('description') or item.findtext('summary') or item.findtext('content') or '').strip()
                or (item.findtext(_atom_ns('summary')) or '').strip()
            )
            link = extract_item_link(item, desc_raw)
            
            # Try different date field names
            pub_date_str = (
                item.findtext('pubDate') or 
                item.findtext('published') or 
                item.findtext('updated') or 
                item.findtext(_atom_ns('published')) or
                item.findtext(_atom_ns('updated')) or
                ''
            ).strip()
            
            description = desc_raw
            # Clean HTML from description
            description = html.unescape(description) if description else ''
            description = re.sub(r"<[^>]+>", "", description)
            description = description[:2000] + "..." if len(description) > 2000 else description
            
            # Parse date
            pub_date = None
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %Z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S%z',
                '%a, %d %b %Y %H:%M:%S',
            ]
            for fmt in date_formats:
                try:
                    pub_date = datetime.strptime(pub_date_str[:25], fmt)
                    break
                except Exception:
                    pass
            
            if not item_in_date_window(pub_date, days_ago):
                continue
            
            # Filter by AI keywords（专用 AI 垂直源可 accept_all）
            if config.get("accept_all") or is_ai_related(title, description, config["ai_keywords"]):
                results.append({
                    'title': html.unescape(title) if isinstance(title, str) else title,
                    'link': link,
                    'date': pub_date,
                    'description': description,
                    'source': source_id,
                    'source_name': config["name"]
                })
        
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "results": results, "count": len(results)}
        
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}

def format_output(source_results, filter_sites=None):
    """Format all results into readable output."""
    output = []
    total = 0

    region_title = {
        "china": "## 🇨🇳 中国境内源",
        "overseas": "## 🌍 境外源",
    }
    for region in ("china", "overseas"):
        region_lines = []
        for source_id in AI_REGION_ORDER.get(region, []):
            if filter_sites and source_id not in filter_sites:
                continue
            result = source_results.get(source_id)
            if not result or result["count"] == 0:
                continue
            icon = result["icon"]
            name = result["name"]
            items = result["results"]
            if "error" in result:
                region_lines.append(f"{icon} **{name}** · ❌ {result['error']}")
                region_lines.append("")
                continue
            total += len(items)
            region_lines.extend(
                format_source_block(
                    icon,
                    f"{name}（{len(items)} 条）",
                    items,
                    max_items=10,
                    desc_max=480,
                    im_clickable=True,
                )
            )
            region_lines.append("")
        if region_lines:
            output.append(region_title[region])
            output.append("")
            output.extend(region_lines)

    if total == 0:
        return "今日无AI相关新资讯。"
    
    header = f"📈 **AI / 技术资讯** · 共 {total} 条\n"
    return header + "\n".join(output).rstrip()

if __name__ == "__main__":
    argv, cli_cap = parse_argv_max_sources(sys.argv[1:])
    max_cap = resolve_max_sources(cli_cap)
    days = DEFAULT_NEWS_LOOKBACK_DAYS
    filter_sites = {"en", "cn"}  # Default: InfoQ only
    
    if len(argv) > 0:
        if argv[0].isdigit():
            days = int(argv[0])
    
    if len(argv) > 1:
        raw_filter = argv[1]
        if raw_filter == "all":
            filter_sites = set(SOURCES.keys())
        else:
            filter_sites = set(raw_filter.replace(" ", "").split(","))
    
    order_keys = [k for k in AI_NEWS_SOURCE_ORDER if k in filter_sites]
    order_keys = apply_source_cap(order_keys, max_cap)
    
    results = {}
    for source_id in order_keys:
        results[source_id] = fetch_source(source_id, SOURCES[source_id], days)
    
    out = format_output(results, filter_sites)
    if max_cap is not None:
        out = f"（本 run 抓取 {len(order_keys)} 个源，上限 {max_cap}）\n\n" + out

    appendix_on = (os.environ.get("OPENCLAW_TECH_RSS_URL_APPENDIX") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    if appendix_on and "今日无AI相关新资讯" not in out:
        max_u = 300
        raw_max = (os.environ.get("OPENCLAW_TECH_RSS_URL_APPENDIX_MAX") or "").strip()
        if raw_max.isdigit():
            max_u = max(1, min(2000, int(raw_max)))
        urls = collect_urls_from_results(results, order_keys, max_urls=max_u)
        out += format_url_appendix_block(urls)

    print(out)
