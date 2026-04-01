#!/usr/bin/env python3
"""
Unified global news fetcher (self-contained).
Usage: python3 fetch_global_news.py [days_ago] [category] [--max-sources N]
       默认 days_ago=3（约过去 72 小时内，滚动窗口）。
入口: 使用 Python 3 直接运行本文件（无需 shell 包装），例如: python3 fetch_global_news.py
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
from news_fetch_filters import (
    DEFAULT_NEWS_LOOKBACK_DAYS,
    apply_source_cap,
    item_in_date_window,
    parse_argv_max_sources,
    resolve_max_sources,
)
from news_format import collect_urls_from_results, format_source_block, format_url_appendix_block
from global_news_sources import CAT_NAMES, FETCH_ORDER, SOURCES, SUPPORTED_CATEGORIES
from rss_links import extract_item_link


def parse_args(argv: List[str]) -> Tuple[int, str, Optional[int]]:
    days = DEFAULT_NEWS_LOOKBACK_DAYS
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
            desc_raw = (
                item.findtext("description")
                or item.findtext("summary")
                or item.findtext("content")
                or item.findtext("content:encoded")
                or ""
            ).strip()
            link = extract_item_link(item, desc_raw)
            desc = re.sub(r"<[^>]+>", "", html.unescape(desc_raw))[:1200]
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
        blocks.extend(
            format_source_block(
                result["icon"],
                f"{result['name']}（{len(items)} 条）",
                items,
                max_items=8,
                desc_max=480,
                im_clickable=True,
            )
        )
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
    overseas_rows = [(sid, results[sid]) for sid in selected if SOURCES[sid]["bucket"] == "overseas" and results.get(sid)]

    pieces: List[str] = [f"{CAT_NAMES.get(category, '📋 全部资讯')} {datetime.now().strftime('%m-%d')}"]
    china_body = format_section("## 🇨🇳 国内与中文源", china_rows) if china_rows else ""
    world_body = format_section("## 🌍 境外主流源", overseas_rows) if overseas_rows and should_show_world_bucket(category) else ""
    if china_body:
        pieces.append(china_body)
    if world_body:
        pieces.append(world_body)

    out = "\n\n".join([p for p in pieces if p]).strip()
    if not out:
        out = "📭 暂无相关资讯"
    if cap is not None:
        out = f"（本 run 抓取 {len(selected)} 个源，上限 {cap}）\n\n" + out

    # 文末纯文本 URL 汇总：即使上游只摘标题，也便于用户搜索 https:// 或整段转发
    appendix_on = (os.environ.get("OPENCLAW_GLOBAL_NEWS_URL_APPENDIX") or "1").strip().lower() not in ("0", "false", "no", "off")
    if appendix_on and out != "📭 暂无相关资讯":
        max_u = 300
        raw_max = (os.environ.get("OPENCLAW_GLOBAL_NEWS_URL_APPENDIX_MAX") or "").strip()
        if raw_max.isdigit():
            max_u = max(1, min(2000, int(raw_max)))
        urls = collect_urls_from_results(results, selected, max_urls=max_u)
        out += format_url_appendix_block(urls)

    print(out)


if __name__ == "__main__":
    main()
