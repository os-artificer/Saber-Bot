"""
Extract canonical article URL from RSS 2.0 <item> or Atom <entry>.
Handles namespaced tags and <link href="..."/> (Atom).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Optional

_ATOM = "{http://www.w3.org/2005/Atom}"


def _first_http_from_description(html: str) -> str:
    if not html:
        return ""
    m = re.search(r'href=["\'](https?://[^"\']+)["\']', html, re.I)
    return (m.group(1) or "").strip() if m else ""


def extract_item_link(item: ET.Element, description: str = "") -> str:
    """
    Return article URL from RSS/Atom item, or '' if unknown.
    """
    # RSS 2.0 plain <link>text</link>
    t = (item.findtext("link") or "").strip()
    if t.startswith("http://") or t.startswith("https://"):
        return t.split("?")[0]

    # Atom: <link href="..." rel="alternate"/>
    for ln in item.findall(_ATOM + "link"):
        href = (ln.get("href") or "").strip()
        rel = (ln.get("rel") or "alternate").lower()
        if href and rel in ("alternate", "", "self"):
            return href.split("?")[0]
    for ln in item.findall("link"):
        href = (ln.get("href") or "").strip()
        if href:
            return href.split("?")[0]

    # Any-namespace link child (some feeds use default xmlns)
    for child in list(item):
        tag = child.tag
        if tag.endswith("}link") or tag == "link":
            txt = (child.text or "").strip()
            if txt.startswith("http"):
                return txt.split("?")[0]
            href = (child.get("href") or "").strip()
            if href:
                return href.split("?")[0]

    guid = (item.findtext("guid") or "").strip()
    if guid.startswith("http://") or guid.startswith("https://"):
        return guid.split("?")[0]

    aid = (item.findtext(_ATOM + "id") or "").strip()
    if aid.startswith("http://") or aid.startswith("https://"):
        return aid.split("?")[0]

    return _first_http_from_description(description or "")
