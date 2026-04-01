#!/usr/bin/env python3
"""
Fetch programming language news, version logs, and open source product info.
推荐入口: bash fetch_dev_news.sh — 优先本脚本，失败则自动 fetch_dev_news.bash.sh。
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

# Programming Language Sources
LANG_SOURCES = {
    "python": {
        "name": "Python",
        "url": "https://blog.python.org/feeds/posts/default",
        "icon": "🐍",
        "org": "Python Software Foundation",
        "desc": "通用编程语言，数据科学/AI首选"
    },
    "rust": {
        "name": "Rust",
        "url": "https://blog.rust-lang.org/feed.xml",
        "icon": "🦀",
        "org": "Rust Foundation",
        "desc": "系统编程语言，主打内存安全"
    },
    "typescript": {
        "name": "TypeScript",
        "url": "https://devblogs.microsoft.com/typescript/feed/",
        "icon": "📘",
        "org": "Microsoft",
        "desc": "JavaScript超集，静态类型"
    },
    "nodejs": {
        "name": "Node.js",
        "url": "https://nodejs.org/en/feed/blog.xml",
        "icon": "🟢",
        "org": "OpenJS Foundation",
        "desc": "JavaScript运行时"
    },
    "golang": {
        "name": "Go",
        "url": "https://go.dev/blog/index.xml",
        "icon": "🔵",
        "org": "Google",
        "desc": "Google开发的编译型语言"
    },
    "java": {
        "name": "Java",
        "url": "https://www.oracle.com/java/technologies/javadoc-and-docs.html",
        "icon": "☕",
        "org": "Oracle / OpenJDK",
        "desc": "企业级后端开发"
    },
    "ruby": {
        "name": "Ruby",
        "url": "https://ruby.social/@RubyWeekly/feed",
        "icon": "💎",
        "org": "Ruby Association",
        "desc": "简洁web开发语言"
    },
    "swift": {
        "name": "Swift",
        "url": "https://swift.org/blog/swift-5.9-released/",
        "icon": "🍎",
        "org": "Apple",
        "desc": "iOS/macOS开发语言"
    },
    "kotlin": {
        "name": "Kotlin",
        "url": "https://blog.jetbrains.com/kotlin/feed/",
        "icon": "🟣",
        "org": "JetBrains / Google",
        "desc": "JVM语言，Android首选"
    },
    "csharp": {
        "name": "C#",
        "url": "https://devblogs.microsoft.com/dotnet/feed/",
        "icon": "💜",
        "org": "Microsoft",
        "desc": ".NET平台主语言"
    }
}

# Open Source & DevTools Sources
OSS_SOURCES = {
    "github": {
        "name": "GitHub Blog",
        "url": "https://github.com/blog.atom",
        "icon": "🐙",
        "desc": "全球最大代码托管平台动态"
    },
    "producthunt": {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com/feed",
        "icon": "🚀",
        "desc": "新产品与工具发布"
    },
    "infoq_feed": {
        "name": "InfoQ（聚合 feed）",
        "url": "https://feed.infoq.com/",
        "icon": "📚",
        "desc": "InfoQ 英文站聚合 RSS"
    },
    "thenewstack": {
        "name": "The New Stack",
        "url": "https://thenewstack.io/feed/",
        "icon": "☁️",
        "desc": "云原生与基础设施"
    },
    "oschina": {
        "name": "OSCHINA",
        "url": "https://www.oschina.net/news/rss",
        "icon": "🐼",
        "desc": "中文开源技术资讯"
    },
    "docker": {
        "name": "Docker Blog",
        "url": "https://blog.docker.com/feed/",
        "icon": "🐳",
        "desc": "容器化技术领导者"
    },
    "kubernetes": {
        "name": "Kubernetes",
        "url": "https://kubernetes.io/feed.xml",
        "icon": "☸️",
        "desc": "容器编排平台"
    },
    "spring": {
        "name": "Spring",
        "url": "https://spring.io/blog.atom",
        "icon": "🌱",
        "desc": "Java企业级框架"
    },
    "react": {
        "name": "React",
        "url": "https://react.dev/blog/rss.xml",
        "icon": "⚛️",
        "desc": "UI构建库"
    },
    "vue": {
        "name": "Vue.js",
        "url": "https://blog.vuejs.org/feed.xml",
        "icon": "💚",
        "desc": "渐进式前端框架"
    },
    "deno": {
        "name": "Deno",
        "url": "https://deno.com/blog/rss.xml",
        "icon": "🦕",
        "desc": "安全 JS/TS 运行时"
    },
    "svelte": {
        "name": "Svelte",
        "url": "https://svelte.dev/blog/rss.xml",
        "icon": "🔥",
        "desc": "编译型前端框架"
    },
    "angular": {
        "name": "Angular",
        "url": "https://blog.angular.io/feed.atom",
        "icon": "📐",
        "desc": "Google前端框架"
    },
    "linux": {
        "name": "Linux",
        "url": "https://lkml.org/lkml/recent.xml",
        "icon": "🐧",
        "desc": "开源内核"
    },
    "vscode": {
        "name": "VS Code",
        "url": "https://code.visualstudio.com/feed.xml",
        "icon": "📎",
        "desc": "微软轻量级编辑器"
    },
    "postgresql": {
        "name": "PostgreSQL",
        "url": "https://www.postgresql.org/blogs/rss/",
        "icon": "🐘",
        "desc": "开源关系型数据库"
    }
}

# Dev Community Sources
DEV_SOURCES = {
    "devto": {
        "name": "dev.to",
        "url": "https://dev.to/feed",
        "icon": "👨‍💻",
        "desc": "开发者社区博客"
    },
    "hackernews": {
        "name": "Hacker News（首页）",
        "url": "https://hnrss.org/frontpage",
        "icon": "👾",
        "desc": "HN 热门（hnrss frontpage）"
    },
    "hn_show": {
        "name": "Hacker News（Show）",
        "url": "https://hnrss.org/show",
        "icon": "🎬",
        "desc": "HN Show 分区"
    },
    "kr36": {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "icon": "⚡",
        "desc": "科技与创业热点"
    },
    "lobsters": {
        "name": "Lobsters",
        "url": "https://lobste.rs/rss",
        "icon": "🦞",
        "desc": "技术社区"
    }
}

# All sources combined
ALL_SOURCES = {}
ALL_SOURCES.update(LANG_SOURCES)
ALL_SOURCES.update(OSS_SOURCES)
ALL_SOURCES.update(DEV_SOURCES)

DEV_LANG_ORDER = [
    "python", "rust", "typescript", "nodejs", "golang", "java", "kotlin", "csharp", "swift", "ruby",
]
DEV_OSS_ORDER = [
    "github",
    "producthunt",
    "infoq_feed",
    "thenewstack",
    "oschina",
    "docker",
    "kubernetes",
    "spring",
    "react",
    "vue",
    "angular",
    "deno",
    "svelte",
    "linux",
    "vscode",
    "postgresql",
]
DEV_COMM_ORDER = ["devto", "hackernews", "hn_show", "kr36", "lobsters"]


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
        
        if "error" in result:
            output.append(f"\n{icon} **{name}** ({org}): ❌ {result['error']}")
            continue
        
        output.append(f"\n{icon} **{name}** — {org}")
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
        
        if "error" in result:
            output.append(f"\n{icon} **{name}**: ❌ {result['error']}")
            continue
        
        output.append(f"\n{icon} **{name}** — {desc}")
        
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
        
        if "error" in result:
            output.append(f"\n{icon} **{name}**: ❌ {result['error']}")
            continue
        
        output.append(f"\n{icon} **{name}** — {desc}")
        
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
