"""
Shared filters for news fetch scripts:
- Date window: drop items without parseable pub date or older than the window.
- Source cap: limit how many feeds/APIs are fetched per run (priority order).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from typing import List, Optional, Sequence


def normalize_naive_local(dt: datetime) -> datetime:
    """Strip tzinfo after converting to local, for naive comparisons."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone().replace(tzinfo=None)


def item_in_date_window(
    pub_date: Optional[datetime],
    days_ago: int,
    *,
    now: Optional[datetime] = None,
) -> bool:
    """
    Return True if the item should be kept.

    - days_ago < 0: no date filter (keep even without pub_date).
    - days_ago == 0: keep only items from **today** (local calendar day), pub_date required.
    - days_ago > 0: keep items with pub_date >= now - days_ago; pub_date required.

    Items without a parseable date are dropped whenever days_ago >= 0.
    """
    if days_ago < 0:
        return True
    if pub_date is None:
        return False
    now = now or datetime.now()
    pd = normalize_naive_local(pub_date)
    if days_ago == 0:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return pd >= start
    cutoff = now - timedelta(days=days_ago)
    return pd >= cutoff


def max_sources_limit() -> Optional[int]:
    """
    Read OPENCLAW_NEWS_MAX_SOURCES (positive int = cap; unset or 0 = unlimited).
    """
    raw = (os.environ.get("OPENCLAW_NEWS_MAX_SOURCES") or "").strip()
    if not raw or not raw.isdigit():
        return None
    n = int(raw)
    return n if n > 0 else None


def apply_source_cap(order: Sequence[str], cap: Optional[int]) -> List[str]:
    """Return first `cap` ids from `order` if cap is set; else full list (deduped)."""
    seen: set[str] = set()
    out: List[str] = []
    for x in order:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    if cap is None:
        return out
    return out[:cap]


def parse_argv_max_sources(argv: List[str]) -> tuple[List[str], Optional[int]]:
    """
    Remove --max-sources N or --max-sources=N from argv; return (rest, cap or None).
    """
    cap: Optional[int] = None
    rest: List[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        m = re.match(r"^--max-sources=(\d+)$", a)
        if m:
            cap = int(m.group(1))
            i += 1
            continue
        if a == "--max-sources" and i + 1 < len(argv) and argv[i + 1].isdigit():
            cap = int(argv[i + 1])
            i += 2
            continue
        rest.append(a)
        i += 1
    if cap is not None and cap <= 0:
        cap = None
    return rest, cap


def resolve_max_sources(cli_cap: Optional[int]) -> Optional[int]:
    """CLI --max-sources overrides env when both set; env used if CLI unset."""
    if cli_cap is not None:
        return cli_cap
    return max_sources_limit()
