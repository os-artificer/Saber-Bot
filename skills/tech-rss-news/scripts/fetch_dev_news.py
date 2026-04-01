#!/usr/bin/env python3
"""
Fetch programming language news, version logs, and open source product info.
入口: python3 fetch_dev_news.py（跨平台，不依赖 Bash）。
Usage: python3 fetch_dev_news.py [days_ago] [category]
    days_ago: number of days to look back (default: 3 ≈ past 72 hours rolling)
    category: all, languages, oss, devtools (default: all)
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
    DEFAULT_NEWS_LOOKBACK_DAYS,
    apply_source_cap,
    item_in_date_window,
    parse_argv_max_sources,
    resolve_max_sources,
)
from rss_links import extract_item_link
from news_format import (
    RULE,
    collect_urls_from_results,
    format_news_item_lines,
    format_url_appendix_block,
)
from tech_rss_dev_sources import ALL_SOURCES, DEV_COMM_ORDER, DEV_LANG_ORDER, DEV_OSS_ORDER, DEV_SOURCES, LANG_SOURCES, OSS_SOURCES


def dev_fetch_order(category: str) -> list:
    """抓取顺序（与展示分区一致）。"""
    if category == "languages":
        return [k for k in DEV_LANG_ORDER if k in LANG_SOURCES]
    if category == "oss":
        return [k for k in DEV_OSS_ORDER if k in OSS_SOURCES]
    if category == "devtools":
        return [k for k in DEV_COMM_ORDER if k in DEV_SOURCES]
    seen: set[str] = set()
    out: list[str] = []
    for seq in (DEV_LANG_ORDER, DEV_OSS_ORDER, DEV_COMM_ORDER):
        for k in seq:
            if k in ALL_SOURCES and k not in seen:
                seen.add(k)
                out.append(k)
    for k in ALL_SOURCES:
        if k not in seen:
            out.append(k)
    return out


def fetch_source(source_id, config, days_ago=None):
    """Fetch news from a single source."""
    if days_ago is None:
        days_ago = DEFAULT_NEWS_LOOKBACK_DAYS
    try:
        req = urllib.request.Request(config["url"], headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode('utf-8')
        
        root = ET.fromstring(content)
        items = root.findall('.//entry') or root.findall('.//item') or []
        
        results = []
        
        for item in items:
            title = (item.findtext('title') or '').strip()
            if not title:
                continue
            
            desc_raw = (
                item.findtext('summary') or
                item.findtext('content') or
                item.findtext('description') or
                item.findtext('content:encoded') or
                ''
            ).strip()
            link = extract_item_link(item, desc_raw)

            pub_date_str = (
                item.findtext('published') or 
                item.findtext('updated') or 
                item.findtext('pubDate') or 
                item.findtext('dc:date') or
                ''
            ).strip()
            
            description = desc_raw
            description = html.unescape(description) if description else ''
            description = re.sub(r'<[^>]+>', '', description)
            description = description[:1200] + '...' if len(description) > 1200 else description
            
            # Parse date
            pub_date = None
            date_formats = [
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S%z',
                '%a, %d %b %Y %H:%M:%S %Z',
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
        
        return {
            "source": source_id, 
            "name": config["name"], 
            "icon": config["icon"], 
            "org": config.get("org", ""),
            "desc": config.get("desc", ""),
            "region": config.get("region", "overseas"),
            "results": results, 
            "count": len(results)
        }
        
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}

def format_output_lang(source_results):
    """Format programming language section."""
    output = ["\n### 🐍 编程语言动态"]
    
    lang_order = DEV_LANG_ORDER
    
    for source_id in lang_order:
        if source_id not in source_results:
            continue
        result = source_results[source_id]
        if not result or result["count"] == 0:
            continue
        
        icon = result["icon"]
        name = result["name"]
        org = result.get("org", "")
        desc = result.get("desc", "")
        region = "境内" if result.get("region") == "china" else "境外"
        
        if "error" in result:
            output.append(f"\n{icon} **{name}** ({org}): ❌ {result['error']}")
            continue
        
        output.append(f"\n{icon} **{name}**（{region}）— {org}")
        output.append(f"   📝 {desc}")
        
        for idx, item in enumerate(result["results"][:3], 1):
            output.append("")
            output.append(RULE)
            output.extend(
                format_news_item_lines(
                    idx,
                    item.get("title") or "",
                    item.get("description") or "",
                    item["date"] if isinstance(item.get("date"), datetime) else None,
                    item.get("link") or "",
                    desc_max=480,
                    im_clickable=True,
                )
            )
    
    return '\n'.join(output)

def format_output_oss(source_results):
    """Format open source tools section."""
    output = ["\n### 🛠️ 开源产品/工具动态"]
    
    oss_order = DEV_OSS_ORDER
    
    for source_id in oss_order:
        if source_id not in source_results:
            continue
        result = source_results[source_id]
        if not result or result["count"] == 0:
            continue
        
        icon = result["icon"]
        name = result["name"]
        desc = result.get("desc", "")
        region = "境内" if result.get("region") == "china" else "境外"
        
        if "error" in result:
            output.append(f"\n{icon} **{name}**: ❌ {result['error']}")
            continue
        
        output.append(f"\n{icon} **{name}**（{region}）— {desc}")
        
        for idx, item in enumerate(result["results"][:3], 1):
            output.append("")
            output.append(RULE)
            output.extend(
                format_news_item_lines(
                    idx,
                    item.get("title") or "",
                    item.get("description") or "",
                    item["date"] if isinstance(item.get("date"), datetime) else None,
                    item.get("link") or "",
                    desc_max=480,
                    im_clickable=True,
                )
            )
    
    return '\n'.join(output)

def format_output_dev(source_results):
    """Format developer community section."""
    output = ["\n### 👨‍💻 开发者社区热点"]
    
    dev_order = DEV_COMM_ORDER
    
    for source_id in dev_order:
        if source_id not in source_results:
            continue
        result = source_results[source_id]
        if not result or result["count"] == 0:
            continue
        
        icon = result["icon"]
        name = result["name"]
        desc = result.get("desc", "")
        region = "境内" if result.get("region") == "china" else "境外"
        
        if "error" in result:
            output.append(f"\n{icon} **{name}**: ❌ {result['error']}")
            continue
        
        output.append(f"\n{icon} **{name}**（{region}）— {desc}")
        
        for idx, item in enumerate(result["results"][:5], 1):
            output.append("")
            output.append(RULE)
            output.extend(
                format_news_item_lines(
                    idx,
                    item.get("title") or "",
                    item.get("description") or "",
                    item["date"] if isinstance(item.get("date"), datetime) else None,
                    item.get("link") or "",
                    desc_max=480,
                    im_clickable=True,
                )
            )
    
    return '\n'.join(output)

def format_output_all(source_results, days=None):
    """Format complete output."""
    if days is None:
        days = DEFAULT_NEWS_LOOKBACK_DAYS
    total = sum(r["count"] for r in source_results.values() if "count" in r)
    
    header = f"# 💻 编程语言 & 开源动态（近{days}天）\n"
    header += f"📊 共获取 {total} 条更新\n"
    
    parts = [header]
    parts.append(format_output_lang(source_results))
    parts.append(format_output_oss(source_results))
    parts.append(format_output_dev(source_results))
    
    return '\n'.join(parts)

if __name__ == "__main__":
    days = DEFAULT_NEWS_LOOKBACK_DAYS
    category = "all"
    argv, cli_cap = parse_argv_max_sources(sys.argv[1:])
    max_cap = resolve_max_sources(cli_cap)
    
    if len(argv) > 0:
        if argv[0].isdigit():
            days = int(argv[0])
    
    if len(argv) > 1:
        category = argv[1].lower()
    
    # Select sources based on category
    if category == "languages":
        sources = LANG_SOURCES
    elif category == "oss":
        sources = OSS_SOURCES
    elif category == "devtools":
        sources = DEV_SOURCES
    else:
        sources = ALL_SOURCES
    
    fetch_ids = dev_fetch_order(category)
    fetch_ids = [k for k in fetch_ids if k in sources]
    fetch_ids = apply_source_cap(fetch_ids, max_cap)
    
    results = {}
    for source_id in fetch_ids:
        results[source_id] = fetch_source(source_id, sources[source_id], days)
    
    out = format_output_all(results, days)
    if max_cap is not None:
        out = f"（本 run 抓取 {len(fetch_ids)} 个源，上限 {max_cap}）\n\n" + out

    appendix_on = (os.environ.get("OPENCLAW_TECH_RSS_URL_APPENDIX") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    if appendix_on and sum(r.get("count", 0) for r in results.values() if isinstance(r, dict)) > 0:
        max_u = 300
        raw_max = (os.environ.get("OPENCLAW_TECH_RSS_URL_APPENDIX_MAX") or "").strip()
        if raw_max.isdigit():
            max_u = max(1, min(2000, int(raw_max)))
        urls = collect_urls_from_results(results, fetch_ids, max_urls=max_u)
        out += format_url_appendix_block(urls)

    print(out)
