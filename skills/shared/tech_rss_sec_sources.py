"""
Security RSS source configuration.
"""

from __future__ import annotations

from typing import Any, Dict, List

SECURITY_NEWS: Dict[str, Dict[str, Any]] = {
    "thn": {"name": "The Hacker News", "url": "https://thehackernews.com/feeds/posts/default?security", "icon": "🎯", "desc": "全球最权威网络安全媒体之一", "region": "overseas"},
    "bleeping": {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "icon": "💻", "desc": "知名网络安全新闻站", "region": "overseas"},
    "securityweek": {"name": "SecurityWeek", "url": "https://www.securityweek.com/feed/", "icon": "📰", "desc": "企业安全新闻", "region": "overseas"},
    "krebson": {"name": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/", "icon": "🔍", "desc": "Brian Krebs独立网络安全调查", "region": "overseas"},
    "darkreading": {"name": "Dark Reading", "url": "https://www.darkreading.com/rss.xml", "icon": "🌑", "desc": "企业安全分析与战略", "region": "overseas"},
    "threatpost": {"name": "Threatpost", "url": "https://threatpost.com/feed/", "icon": "⚠️", "desc": "独立网络安全新闻", "region": "overseas"},
    "nakedsecurity": {"name": "Naked Security", "url": "https://nakedsecurity.sophos.com/feed/", "icon": "🕵️", "desc": "Sophos安全研究", "region": "overseas"},
    "helpnet": {"name": "Help Net Security", "url": "https://www.helpnetsecurity.com/feed/", "icon": "🔐", "desc": "网络安全新闻与研究", "region": "overseas"},
    "schneier": {"name": "Schneier on Security", "url": "https://www.schneier.com/feed/atom/", "icon": "🛡️", "desc": "Bruce Schneier安全专家博客", "region": "overseas"},
    "isc_sans": {"name": "SANS ISC Diary", "url": "https://isc.sans.edu/rssfeed_full.xml", "icon": "📡", "desc": "SANS互联网风暴中心日记（全文 RSS）", "region": "overseas"},
    "securelist": {"name": "Kaspersky Securelist", "url": "https://securelist.com/feed/", "icon": "🕸️", "desc": "卡巴斯基威胁研究", "region": "overseas"},
    "welivesecurity": {"name": "ESET WeLiveSecurity", "url": "https://www.welivesecurity.com/feed/", "icon": "🦠", "desc": "ESET 安全研究与资讯", "region": "overseas"},
    "rapid7": {"name": "Rapid7 Blog", "url": "https://blog.rapid7.com/rss/", "icon": "⚡", "desc": "漏洞与检测研究", "region": "overseas"},
    "recordedfuture": {"name": "Recorded Future", "url": "https://www.recordedfuture.com/feed/", "icon": "🔮", "desc": "威胁情报与网络风险", "region": "overseas"},
    "anquanke": {"name": "安全客", "url": "https://www.anquanke.com/rss", "icon": "🔰", "desc": "国内安全资讯与漏洞动态", "region": "china"},
    "freebuf": {"name": "FreeBuf", "url": "https://www.freebuf.com/feed", "icon": "🧱", "desc": "网络安全行业门户", "region": "china"},
    "nsfocus": {"name": "绿盟科技博客", "url": "https://blog.nsfocus.net/feed/", "icon": "🟢", "desc": "绿盟威胁研究与安全公告", "region": "china"},
}

VULN_SOURCES: Dict[str, Dict[str, Any]] = {
    "tenable": {"name": "Tenable Blog", "url": "https://www.tenable.com/blog/feed", "icon": "🕵️", "desc": "漏洞研究与分析", "region": "overseas"},
    "qualys": {"name": "Qualys Blog", "url": "https://blog.qualys.com/feed", "icon": "🏆", "desc": "Qualys漏洞研究", "region": "overseas"},
    "exploitdb": {"name": "Exploit-DB", "url": "https://www.exploit-db.com/rss.xml", "icon": "💉", "desc": "漏洞利用代码数据库", "region": "overseas"},
    "unit42": {"name": "Palo Alto Unit 42", "url": "https://unit42.paloaltonetworks.com/feed/", "icon": "🦅", "desc": "高级威胁研究", "region": "overseas"},
    "nvd": {"name": "NVD CVE（recent JSON）", "url": "", "kind": "json_nvd", "icon": "🛡️", "desc": "NIST NVD 近期 CVE 官方 JSON 源（gzip）", "region": "overseas"},
    "cisa_kev": {"name": "CISA KEV", "url": "", "kind": "json_cisa_kev", "icon": "🇺🇸", "desc": "CISA 已知被利用漏洞目录（JSON）", "region": "overseas"},
}

SE_SOURCES: Dict[str, Dict[str, Any]] = {
    "socialengineer": {"name": "Social-Engineer.org", "url": "https://www.social-engineer.org/feed/", "icon": "🎭", "desc": "社会工程学权威资源", "region": "overseas"},
    "trustsec": {"name": "TrustedSec", "url": "https://www.trustedsec.com/feed/", "icon": "✅", "desc": "渗透测试与社会工程", "region": "overseas"},
    "offsec": {"name": "Offensive Security", "url": "https://www.offensive-security.com/feed/", "icon": "⚔️", "desc": "渗透测试培训与研究", "region": "overseas"},
}

TOOLS_SOURCES: Dict[str, Dict[str, Any]] = {
    "crowdstrike": {"name": "CrowdStrike", "url": "https://www.crowdstrike.com/blog/feed/", "icon": "🦅", "desc": "端点安全与威胁情报", "region": "overseas"},
    "sentinelone": {"name": "SentinelOne", "url": "https://www.sentinelone.com/feed/", "icon": "1️⃣", "desc": "AI端点保护", "region": "overseas"},
    "mandiant": {"name": "Mandiant", "url": "https://www.mandiant.com/feed", "icon": "🔥", "desc": "APT威胁研究", "region": "overseas"},
    "csoonline": {"name": "CSO Online", "url": "https://www.csoonline.com/rss/security/", "icon": "🏢", "desc": "企业安全战略", "region": "overseas"},
}

ALL_SOURCES: Dict[str, Dict[str, Any]] = {}
ALL_SOURCES.update(SECURITY_NEWS)
ALL_SOURCES.update(VULN_SOURCES)
ALL_SOURCES.update(SE_SOURCES)
ALL_SOURCES.update(TOOLS_SOURCES)

SEC_FETCH_ORDER: Dict[str, List[str]] = {
    "all": ["thn", "bleeping", "securityweek", "krebson", "darkreading", "threatpost", "nakedsecurity", "helpnet", "schneier", "isc_sans", "securelist", "welivesecurity", "rapid7", "recordedfuture", "anquanke", "freebuf", "nsfocus", "nvd", "cisa_kev", "tenable", "qualys", "exploitdb", "unit42", "socialengineer", "trustsec", "offsec", "crowdstrike", "sentinelone", "mandiant", "csoonline"],
    "vulns": ["nvd", "cisa_kev", "anquanke", "freebuf", "nsfocus", "tenable", "qualys", "exploitdb", "unit42"],
    "attacks": ["thn", "bleeping", "securityweek", "krebson", "darkreading", "threatpost", "nakedsecurity", "helpnet", "schneier", "isc_sans", "securelist", "welivesecurity", "rapid7", "recordedfuture", "anquanke", "freebuf", "nsfocus"],
    "se": ["socialengineer", "trustsec", "offsec"],
    "tools": ["crowdstrike", "sentinelone", "mandiant", "csoonline"],
}
