#!/usr/bin/env python3
"""
Fetch cybersecurity news: network penetration, vulnerabilities, attack techniques, and social engineering.
推荐入口: bash fetch_sec_news.sh — 优先本脚本，失败则自动 fetch_sec_news.bash.sh。
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

# === Security News Sources ===
SECURITY_NEWS = {
    "thn": {
        "name": "The Hacker News",
        "url": "https://thehackernews.com/feeds/posts/default?security",
        "icon": "🎯",
        "desc": "全球最权威网络安全媒体之一"
    },
    "bleeping": {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "icon": "💻",
        "desc": "知名网络安全新闻站"
    },
    "securityweek": {
        "name": "SecurityWeek",
        "url": "https://www.securityweek.com/feed/",
        "icon": "📰",
        "desc": "企业安全新闻"
    },
    "krebson": {
        "name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/feed/",
        "icon": "🔍",
        "desc": "Brian Krebs独立网络安全调查"
    },
    "darkreading": {
        "name": "Dark Reading",
        "url": "https://www.darkreading.com/rss.xml",
        "icon": "🌑",
        "desc": "企业安全分析与战略"
    },
    "threatpost": {
        "name": "Threatpost",
        "url": "https://threatpost.com/feed/",
        "icon": "⚠️",
        "desc": "独立网络安全新闻"
    },
    "nakedsecurity": {
        "name": "Naked Security",
        "url": "https://nakedsecurity.sophos.com/feed/",
        "icon": "🕵️",
        "desc": "Sophos安全研究"
    },
    "helpnet": {
        "name": "Help Net Security",
        "url": "https://www.helpnetsecurity.com/feed/",
        "icon": "🔐",
        "desc": "网络安全新闻与研究"
    },
    "schneier": {
        "name": "Schneier on Security",
        "url": "https://www.schneier.com/feed/atom/",
        "icon": "🛡️",
        "desc": "Bruce Schneier安全专家博客"
    },
    "isc_sans": {
        "name": "SANS ISC Diary",
        "url": "https://isc.sans.edu/rssfeed_full.xml",
        "icon": "📡",
        "desc": "SANS互联网风暴中心日记（全文 RSS）"
    },
    "securelist": {
        "name": "Kaspersky Securelist",
        "url": "https://securelist.com/feed/",
        "icon": "🕸️",
        "desc": "卡巴斯基威胁研究"
    },
    "welivesecurity": {
        "name": "ESET WeLiveSecurity",
        "url": "https://www.welivesecurity.com/feed/",
        "icon": "🦠",
        "desc": "ESET 安全研究与资讯"
    },
    "rapid7": {
        "name": "Rapid7 Blog",
        "url": "https://blog.rapid7.com/rss/",
        "icon": "⚡",
        "desc": "漏洞与检测研究"
    },
    "recordedfuture": {
        "name": "Recorded Future",
        "url": "https://www.recordedfuture.com/feed/",
        "icon": "🔮",
        "desc": "威胁情报与网络风险"
    },
    "anquanke": {
        "name": "安全客",
        "url": "https://www.anquanke.com/rss",
        "icon": "🔰",
        "desc": "国内安全资讯与漏洞动态"
    },
    "freebuf": {
        "name": "FreeBuf",
        "url": "https://www.freebuf.com/feed",
        "icon": "🧱",
        "desc": "网络安全行业门户"
    },
    "nsfocus": {
        "name": "绿盟科技博客",
        "url": "https://blog.nsfocus.net/feed/",
        "icon": "🟢",
        "desc": "绿盟威胁研究与安全公告"
    },
}

# === Vulnerability / CVE Sources ===
VULN_SOURCES = {
    "tenable": {
        "name": "Tenable Blog",
        "url": "https://www.tenable.com/blog/feed",
        "icon": "🕵️",
        "desc": "漏洞研究与分析"
    },
    "qualys": {
        "name": "Qualys Blog",
        "url": "https://blog.qualys.com/feed",
        "icon": "🏆",
        "desc": "Qualys漏洞研究"
    },
    "exploitdb": {
        "name": "Exploit-DB",
        "url": "https://www.exploit-db.com/rss.xml",
        "icon": "💉",
        "desc": "漏洞利用代码数据库"
    },
    "unit42": {
        "name": "Palo Alto Unit 42",
        "url": "https://unit42.paloaltonetworks.com/feed/",
        "icon": "🦅",
        "desc": "高级威胁研究"
    },
    "nvd": {
        "name": "NVD CVE（recent JSON）",
        "url": "",
        "kind": "json_nvd",
        "icon": "🛡️",
        "desc": "NIST NVD 近期 CVE 官方 JSON 源（gzip）"
    },
    "cisa_kev": {
        "name": "CISA KEV",
        "url": "",
        "kind": "json_cisa_kev",
        "icon": "🇺🇸",
        "desc": "CISA 已知被利用漏洞目录（JSON）"
    },
}

# === Social Engineering Sources ===
SE_SOURCES = {
    "socialengineer": {
        "name": "Social-Engineer.org",
        "url": "https://www.social-engineer.org/feed/",
        "icon": "🎭",
        "desc": "社会工程学权威资源"
    },
    "trustsec": {
        "name": "TrustedSec",
        "url": "https://www.trustedsec.com/feed/",
        "icon": "✅",
        "desc": "渗透测试与社会工程"
    },
    "offsec": {
        "name": "Offensive Security",
        "url": "https://www.offensive-security.com/feed/",
        "icon": "⚔️",
        "desc": "渗透测试培训与研究"
    }
}

# === Security Tools / Pentest ===
TOOLS_SOURCES = {
    "crowdstrike": {
        "name": "CrowdStrike",
        "url": "https://www.crowdstrike.com/blog/feed/",
        "icon": "🦅",
        "desc": "端点安全与威胁情报"
    },
    "sentinelone": {
        "name": "SentinelOne",
        "url": "https://www.sentinelone.com/feed/",
        "icon": "1️⃣",
        "desc": "AI端点保护"
    },
    "mandiant": {
        "name": "Mandiant",
        "url": "https://www.mandiant.com/feed",
        "icon": "🔥",
        "desc": "APT威胁研究"
    },
    "csoonline": {
        "name": "CSO Online",
        "url": "https://www.csoonline.com/rss/security/",
        "icon": "🏢",
        "desc": "企业安全战略"
    }
}

# All sources
ALL_SOURCES = {}
ALL_SOURCES.update(SECURITY_NEWS)
ALL_SOURCES.update(VULN_SOURCES)
ALL_SOURCES.update(SE_SOURCES)
ALL_SOURCES.update(TOOLS_SOURCES)

# 抓取顺序（与输出分组一致，用于 --max-sources / OPENCLAW_NEWS_MAX_SOURCES）
SEC_FETCH_ORDER = {
    "all": [
        "thn", "bleeping", "securityweek", "krebson", "darkreading", "threatpost",
        "nakedsecurity", "helpnet", "schneier", "isc_sans", "securelist", "welivesecurity",
        "rapid7", "recordedfuture", "anquanke", "freebuf", "nsfocus",
        "nvd", "cisa_kev", "tenable", "qualys", "exploitdb", "unit42",
        "socialengineer", "trustsec", "offsec", "crowdstrike", "sentinelone", "mandiant", "csoonline",
    ],
    "vulns": [
        "nvd", "cisa_kev", "anquanke", "freebuf", "nsfocus",
        "tenable", "qualys", "exploitdb", "unit42",
    ],
    "attacks": [
        "thn", "bleeping", "securityweek", "krebson", "darkreading", "threatpost",
        "nakedsecurity", "helpnet", "schneier", "isc_sans", "securelist", "welivesecurity",
        "rapid7", "recordedfuture", "anquanke", "freebuf", "nsfocus",
    ],
    "se": ["socialengineer", "trustsec", "offsec"],
    "tools": ["crowdstrike", "sentinelone", "mandiant", "csoonline"],
}


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
    
    # Build source order by category
    if category == "all":
        source_order = [
            ("thn", "🎯"), ("bleeping", "💻"), ("securityweek", "📰"),
            ("krebson", "🔍"), ("darkreading", "🌑"), ("threatpost", "⚠️"),
            ("nakedsecurity", "🕵️"), ("helpnet", "🔐"), ("schneier", "🛡️"),
            ("isc_sans", "📡"), ("securelist", "🕸️"), ("welivesecurity", "🦠"),
            ("rapid7", "⚡"), ("recordedfuture", "🔮"),
            ("anquanke", "🔰"), ("freebuf", "🧱"), ("nsfocus", "🟢"),
            ("nvd", "🛡️"), ("cisa_kev", "🇺🇸"),
            ("tenable", "🕵️"), ("qualys", "🏆"), ("exploitdb", "💉"), ("unit42", "🦅"),
            ("socialengineer", "🎭"), ("trustsec", "✅"), ("offsec", "⚔️"),
            ("crowdstrike", "🦅"), ("sentinelone", "1️⃣"), ("mandiant", "🔥"), ("csoonline", "🏢"),
        ]
    elif category == "vulns":
        source_order = [
            ("nvd", "🛡️"), ("cisa_kev", "🇺🇸"),
            ("anquanke", "🔰"), ("freebuf", "🧱"), ("nsfocus", "🟢"),
            ("tenable", "🕵️"), ("qualys", "🏆"), ("exploitdb", "💉"), ("unit42", "🦅"),
        ]
    elif category == "attacks":
        source_order = [
            ("thn", "🎯"), ("bleeping", "💻"), ("securityweek", "📰"), ("krebson", "🔍"),
            ("darkreading", "🌑"), ("threatpost", "⚠️"), ("nakedsecurity", "🕵️"),
            ("helpnet", "🔐"), ("schneier", "🛡️"),
            ("isc_sans", "📡"), ("securelist", "🕸️"), ("welivesecurity", "🦠"),
            ("rapid7", "⚡"), ("recordedfuture", "🔮"),
            ("anquanke", "🔰"), ("freebuf", "🧱"), ("nsfocus", "🟢"),
        ]
    elif category == "se":
        source_order = [("socialengineer", "🎭"), ("trustsec", "✅"), ("offsec", "⚔️")]
    elif category == "tools":
        source_order = [("crowdstrike", "🦅"), ("sentinelone", "1️⃣"), ("mandiant", "🔥"), ("csoonline", "🏢")]
    else:
        source_order = [(k, v["icon"]) for k, v in source_results.items()]
    
    output = []
    output.append(f"🔒 安全资讯 {today} | 共 {total} 条")
    output.append("")
    
    prev_group = None
    for source_id, icon in source_order:
        if source_id not in source_results:
            continue
        result = source_results[source_id]
        if not result or result["count"] == 0:
            continue
        
        lines = format_section(icon, source_id, result, max_items=6)
        if not lines:
            continue
        
        # Add blank line between groups
        group = 0
        if source_id in [
            "thn", "bleeping", "securityweek", "krebson", "darkreading", "threatpost",
            "nakedsecurity", "helpnet", "schneier", "isc_sans", "securelist",
            "welivesecurity", "rapid7", "recordedfuture", "anquanke", "freebuf", "nsfocus",
        ]:
            group = 1
        elif source_id in ["nvd", "cisa_kev", "tenable", "qualys", "exploitdb", "unit42"]:
            group = 2
        elif source_id in ["socialengineer", "trustsec", "offsec"]:
            group = 3
        else:
            group = 4
        
        if prev_group and group != prev_group:
            output.append("")
        prev_group = group
        
        output.extend(lines)
    
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
