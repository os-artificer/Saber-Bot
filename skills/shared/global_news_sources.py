"""
Global news source configuration shared by scripts.
"""

from __future__ import annotations

from typing import Any, Dict

SUPPORTED_CATEGORIES = {
    "all",
    "domestic",
    "world",
    "economy",
    "geopolitics",
    "war",
    "politics",
    "tech",
    "security",
    "china",
}

CAT_NAMES = {
    "all": "📋 全部资讯",
    "domestic": "🇨🇳 国内动态",
    "world": "🌐 国际局势",
    "economy": "💹 经济财经",
    "geopolitics": "🌍 地缘政治",
    "war": "⚔️ 战争军事",
    "politics": "🏛️ 政治要闻",
    "tech": "📱 科技数码",
    "security": "🔐 安全资讯",
    "china": "🇨🇳 中国相关",
}

# Combined source list: china/mainland + overseas/mainstream
SOURCES: Dict[str, Dict[str, Any]] = {
    "xinhua_world": {"name": "新华网·国际", "kind": "rss", "url": "http://www.xinhuanet.com/world/news_world.xml", "icon": "🌐", "bucket": "china", "tags": ["all", "world", "geopolitics"]},
    "xinhua_politics": {"name": "新华网·时政", "kind": "rss", "url": "http://www.xinhuanet.com/politics/news_politics.xml", "icon": "🏛️", "bucket": "china", "tags": ["all", "domestic", "politics", "geopolitics"]},
    "xinhua_fortune": {"name": "新华网·财经", "kind": "rss", "url": "http://www.xinhuanet.com/fortune/news_fortune.xml", "icon": "💹", "bucket": "china", "tags": ["all", "economy", "domestic"]},
    "cns_scroll": {"name": "中新网·滚动", "kind": "rss", "url": "https://www.chinanews.com.cn/rss/scroll-news.xml", "icon": "📰", "bucket": "china", "tags": ["all", "domestic", "world", "economy", "geopolitics", "war", "politics"]},
    "huanqiu_cn": {"name": "环球时报（中文）", "kind": "rss", "url": "https://m.huanqiu.com/rss", "icon": "🌏", "bucket": "china", "tags": ["all", "domestic", "world", "politics", "geopolitics"]},
    "huanqiu_gt": {"name": "环球时报 Global Times", "kind": "rss", "url": "https://www.globaltimes.cn/rss/outbrain.xml", "icon": "🗞️", "bucket": "china", "tags": ["all", "world", "china", "geopolitics", "war", "politics"]},
    "people_politics": {"name": "人民网·政治", "kind": "rss", "url": "http://www.people.com.cn/rss/politics.xml", "icon": "🏛️", "bucket": "china", "tags": ["all", "domestic", "politics", "geopolitics"]},
    "ftchinese": {"name": "FT中文网", "kind": "rss", "url": "https://www.ftchinese.com/rss/feed", "icon": "💼", "bucket": "china", "tags": ["all", "world", "economy", "domestic"]},
    "bbc_cn": {"name": "BBC中文网", "kind": "rss", "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml", "icon": "🇬🇧", "bucket": "china", "tags": ["all", "world", "economy", "geopolitics", "war", "politics"]},
    "scmp_cn": {"name": "南华早报", "kind": "rss", "url": "https://www.scmp.com/rss/world.xml", "icon": "🇭🇰", "bucket": "china", "tags": ["all", "world", "economy", "geopolitics", "war"]},
    "sina_domestic": {"name": "新浪国内", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "2516", "num": "20", "page": "1"}, "icon": "🇨🇳", "bucket": "china", "tags": ["all", "domestic", "politics", "economy", "geopolitics"]},
    "sina_world": {"name": "新浪国际", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "2517", "num": "20", "page": "1"}, "icon": "🌐", "bucket": "china", "tags": ["all", "world", "geopolitics", "war"]},
    "sina_economy": {"name": "新浪财经", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "1686", "num": "20", "page": "1"}, "icon": "💹", "bucket": "china", "tags": ["all", "economy", "domestic"]},
    "sina_mil": {"name": "新浪军事", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "2425", "num": "20", "page": "1"}, "icon": "⚔️", "bucket": "china", "tags": ["all", "war", "geopolitics", "domestic"]},
    "sina_tech": {"name": "新浪科技", "kind": "sina", "api_url": "https://feed.mix.sina.com.cn/api/roll/get", "params": {"pageid": "153", "lid": "1195", "num": "20", "page": "1"}, "icon": "📱", "bucket": "china", "tags": ["all", "tech", "economy"]},
    "bbc_world": {"name": "BBC News", "kind": "rss", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "icon": "🇬🇧", "bucket": "overseas", "tags": ["all", "world", "china"]},
    "nytimes_world": {"name": "NY Times World", "kind": "rss", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "icon": "🇺🇸", "bucket": "overseas", "tags": ["all", "world", "china"]},
    "reuters_world": {"name": "Reuters", "kind": "rss", "url": "https://feeds.reuters.com/reuters/worldnews", "icon": "📰", "bucket": "overseas", "tags": ["all", "world"]},
    "bbc_business": {"name": "BBC Business", "kind": "rss", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "icon": "💷", "bucket": "overseas", "tags": ["all", "economy"]},
    "ft": {"name": "Financial Times", "kind": "rss", "url": "https://www.ft.com/rss/home", "icon": "💹", "bucket": "overseas", "tags": ["all", "economy"]},
    "theverge": {"name": "The Verge", "kind": "rss", "url": "https://www.theverge.com/rss/index.xml", "icon": "📱", "bucket": "overseas", "tags": ["all", "tech"]},
    "arstechnica": {"name": "Ars Technica", "kind": "rss", "url": "https://feeds.arstechnica.com/arstechnica/index", "icon": "🔧", "bucket": "overseas", "tags": ["all", "tech"]},
    "wired": {"name": "Wired", "kind": "rss", "url": "https://www.wired.com/feed/rss", "icon": "🔌", "bucket": "overseas", "tags": ["all", "tech"]},
}

FETCH_ORDER = [
    "xinhua_politics",
    "xinhua_fortune",
    "xinhua_world",
    "cns_scroll",
    "huanqiu_cn",
    "huanqiu_gt",
    "people_politics",
    "ftchinese",
    "sina_domestic",
    "sina_world",
    "sina_economy",
    "sina_mil",
    "sina_tech",
    "bbc_cn",
    "scmp_cn",
    "bbc_world",
    "nytimes_world",
    "reuters_world",
    "bbc_business",
    "ft",
    "theverge",
    "arstechnica",
    "wired",
]
