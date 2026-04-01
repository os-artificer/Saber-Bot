#!/usr/bin/env python3
"""
Fetch cybersecurity news: network penetration, vulnerabilities, attack techniques, and social engineering.
入口: python3 fetch_sec_news.py（跨平台，不依赖 Bash）。
Usage: python3 fetch_sec_news.py [days_ago] [category]
    days_ago: number of days to look back (default: 3 ≈ past 72 hours rolling)
    category: all, vulns, attacks, se (social engineering), tools (default: all)
"""

import gzip
import json
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
from tech_rss_sec_sources import ALL_SOURCES, SEC_FETCH_ORDER, SECURITY_NEWS, SE_SOURCES, TOOLS_SOURCES, VULN_SOURCES


def _parse_iso_datetime(s: str):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            if fmt.endswith("%f"):
                return datetime.strptime(s[:26], fmt)
            return datetime.strptime(s[:19], fmt)
        except Exception:
            pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except Exception:
        return None


def _browser_headers() -> dict:
    """NVD / some gov CDNs return 403 for minimal user-agents."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, application/gzip, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }


def fetch_nvd_json(source_id, config, days_ago=None):
    if days_ago is None:
        days_ago = DEFAULT_NEWS_LOOKBACK_DAYS
    """NIST NVD nvdcve-1.1-recent.json.gz"""
    url = (
        (os.environ.get("OPENCLAW_NVD_CVE_GZ_URL") or "").strip()
        or "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"
    )
    try:
        req = urllib.request.Request(url, headers=_browser_headers())
        with urllib.request.urlopen(req, timeout=90) as response:
            raw = response.read()
        text = gzip.decompress(raw).decode("utf-8")
        data = json.loads(text)
        results = []
        for item in data.get("CVE_Items", []):
            pub = item.get("publishedDate") or ""
            pub_date = _parse_iso_datetime(pub)
            if not item_in_date_window(pub_date, days_ago):
                continue
            cve = item.get("cve", {})
            cid = (cve.get("CVE_data_meta") or {}).get("ID", "CVE")
            desc = ""
            for d in (cve.get("description") or {}).get("description_data", []):
                if d.get("lang") in ("en", "eng"):
                    desc = (d.get("value") or "")[:400]
                    break
            if not desc:
                for d in (cve.get("description") or {}).get("description_data", []):
                    desc = (d.get("value") or "")[:400]
                    break
            link = f"https://nvd.nist.gov/vuln/detail/{cid}"
            results.append({
                "title": cid,
                "link": link,
                "date": pub_date,
                "description": desc,
                "source": source_id,
            })
            if len(results) >= 120:
                break
        return {
            "source": source_id,
            "name": config["name"],
            "icon": config["icon"],
            "desc": config.get("desc", ""),
            "results": results,
            "count": len(results),
        }
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}


def fetch_cisa_kev_json(source_id, config, days_ago=None):
    if days_ago is None:
        days_ago = DEFAULT_NEWS_LOOKBACK_DAYS
    """CISA Known Exploited Vulnerabilities JSON."""
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    try:
        req = urllib.request.Request(url, headers=_browser_headers())
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        results = []
        for row in data.get("vulnerabilities", []):
            cve_id = (row.get("cveID") or "").strip()
            title = row.get("vulnerabilityName") or cve_id
            added = row.get("dateAdded") or ""
            if added and "T" not in added:
                try:
                    pub_date = datetime.strptime(added[:10], "%Y-%m-%d")
                except Exception:
                    pub_date = _parse_iso_datetime(added)
            else:
                pub_date = _parse_iso_datetime(added)
            if not item_in_date_window(pub_date, days_ago):
                continue
            vendor = row.get("vendorProject") or ""
            product = row.get("product") or ""
            desc = (row.get("shortDescription") or f"{vendor} / {product}").strip()[:400]
            link = f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id.startswith("CVE-") else "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
            results.append({
                "title": title,
                "link": link,
                "date": pub_date,
                "description": desc,
                "source": source_id,
            })
        return {
            "source": source_id,
            "name": config["name"],
            "icon": config["icon"],
            "desc": config.get("desc", ""),
            "results": results,
            "count": len(results),
        }
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}


def fetch_source(source_id, config, days_ago=None):
    """Fetch news from a single source."""
    if days_ago is None:
        days_ago = DEFAULT_NEWS_LOOKBACK_DAYS
    if config.get("kind") == "json_nvd":
        return fetch_nvd_json(source_id, config, days_ago)
    if config.get("kind") == "json_cisa_kev":
        return fetch_cisa_kev_json(source_id, config, days_ago)
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
            description = description[:400] + '...' if len(description) > 400 else description
            
            # Parse date
            pub_date = None
            date_formats = [
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S%z',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%a, %d %b %Y %H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%d %b %Y %H:%M:%S',
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
            "desc": config.get("desc", ""),
            "results": results, 
            "count": len(results)
        }
        
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}

def format_section(icon, source_id, result, max_items=5):
    """Format a single source's items: 摘要 / 时间 / 链接."""
    if "error" in result:
        return [f"{icon} **{result['name']}** · ❌ {result['error']}"]
    n = result["count"]
    return format_source_block(
        icon,
        f"{result['name']}（{n} 条）",
        result["results"],
        max_items=max_items,
        desc_max=180,
        im_clickable=True,
    )

def format_output_all(source_results, days=None, category="all"):
    """Format complete output - plain text, no markdown."""
    if days is None:
        days = DEFAULT_NEWS_LOOKBACK_DAYS
    total = sum(r["count"] for r in source_results.values() if "count" in r)
    today = datetime.now().strftime('%m-%d')

    order_ids = SEC_FETCH_ORDER.get(category, SEC_FETCH_ORDER["all"])
    output = []
    output.append(f"🔒 安全资讯 {today} | 共 {total} 条")
    output.append("")

    for region, title in (("china", "## 🇨🇳 中国境内源"), ("overseas", "## 🌍 境外源")):
        region_lines = []
        for source_id in order_ids:
            if source_id not in source_results:
                continue
            src_cfg = ALL_SOURCES.get(source_id, {})
            if src_cfg.get("region", "overseas") != region:
                continue
            result = source_results[source_id]
            if not result or result["count"] == 0:
                continue
            icon = result.get("icon", src_cfg.get("icon", "•"))
            lines = format_section(icon, source_id, result, max_items=6)
            if lines:
                region_lines.extend(lines)
                region_lines.append("")
        if region_lines:
            output.append(title)
            output.append("")
            output.extend(region_lines)
    
    return '\n'.join(output)

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
    if category == "vulns":
        sources = VULN_SOURCES
    elif category == "attacks":
        sources = SECURITY_NEWS
    elif category == "se":
        sources = SE_SOURCES
    elif category == "tools":
        sources = TOOLS_SOURCES
    else:
        sources = ALL_SOURCES
    
    order = SEC_FETCH_ORDER.get(category, SEC_FETCH_ORDER["all"])
    fetch_ids = [k for k in order if k in sources]
    fetch_ids = apply_source_cap(fetch_ids, max_cap)
    
    results = {}
    for source_id in fetch_ids:
        results[source_id] = fetch_source(source_id, sources[source_id], days)
    
    out = format_output_all(results, days, category)
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
