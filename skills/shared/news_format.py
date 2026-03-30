"""
Shared output formatting for news-fetch scripts.
Each item: 核心信息摘要、发布时间、原消息链接 — 排版清晰、便于阅读。
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, List, Optional

# 横线分隔（终端/IM 通用）
RULE = "────────────────────────────────────────"


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def core_summary_lines(title: str, description: str = "", *, desc_max: int = 140) -> List[str]:
    """
    核心摘要：标题必显；若 RSS 摘要可用且与标题不重复，则续一行展示摘录。
    """
    t = clean_whitespace(html_unescape_simple(title)) or "（无标题）"
    d = clean_whitespace(html_unescape_simple(description or ""))
    # 去掉与标题高度重复的摘要
    if d and len(d) >= 20:
        if d.lower().startswith(t[: min(20, len(t))].lower()) and len(d) <= len(t) + 5:
            d = ""
        elif t.lower() in d.lower() and len(d) < len(t) + 30:
            d = ""

    lines = [f"摘要 · {t}"]
    if d:
        excerpt = d if len(d) <= desc_max else d[: desc_max - 1].rstrip() + "…"
        lines.append(f"      {excerpt}")
    return lines


def html_unescape_simple(s: str) -> str:
    try:
        import html as _html

        return _html.unescape(s)
    except Exception:
        return s


def format_datetime(dt: Optional[datetime]) -> str:
    if not dt:
        return "未知"
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "未知"


def clean_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    return u.split("?")[0] if "?" in u else u


def format_news_item_lines(
    index: int,
    title: str,
    description: str = "",
    pub_date: Optional[datetime] = None,
    url: str = "",
    *,
    desc_max: int = 140,
) -> List[str]:
    """单条资讯：摘要（可多行）+ 时间 + 链接。"""
    lines: List[str] = []
    lines.append(f"【{index}】")
    lines.extend(core_summary_lines(title, description, desc_max=desc_max))
    lines.append(f"时间 · {format_datetime(pub_date)}")
    link = clean_url(url)
    lines.append(f"链接 · {link if link else '（无）'}")
    return lines


def format_source_block(
    icon: str,
    source_name: str,
    items: List[Any],
    *,
    max_items: int = 10,
    desc_max: int = 140,
) -> List[str]:
    """
    items: dict-like with keys title, link, date (datetime), optional description
    """
    lines: List[str] = []
    lines.append(f"{icon} **{source_name}**")
    n = 0
    idx = 1
    for item in items[:max_items]:
        title = item.get("title") or ""
        desc = item.get("description") or ""
        dt = item.get("date")
        url = item.get("link") or ""
        if n:
            lines.append("")
        lines.append(RULE)
        lines.extend(
            format_news_item_lines(
                idx,
                title,
                desc,
                dt if isinstance(dt, datetime) else None,
                url,
                desc_max=desc_max,
            )
        )
        n += 1
        idx += 1
    return lines
