#!/usr/bin/env python3
"""
Fetch AI/Tech news from multiple authoritative IT news sources.
Usage: python3 fetch_ai_news.py [days_ago] [site_filter]
    days_ago: number of days to look back (default: 0 = today only)
    site_filter: comma-separated list of site codes (e.g., "en,cn,verge")
                 or "all" for everything (default: "en,cn")
    
Site codes:
    en     - InfoQ English (infoq.com)
    cn     - InfoQ 中文 (infoq.cn)
    verge  - The Verge
    ars    - Ars Technica
    tc     - TechCrunch
    wired  - Wired
    hn     - Hacker News
    tns    - The New Stack
    vb     - VentureBeat
    devto  - dev.to
"""

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
    apply_source_cap,
    item_in_date_window,
    parse_argv_max_sources,
    resolve_max_sources,
)
from news_format import format_source_block

# Supported sources with RSS feeds
SOURCES = {
    "en": {
        "name": "InfoQ English",
        "url": "https://www.infoq.com/feed",
        "lang": "en",
        "icon": "🌐",
        "ai_keywords": [
            "ai", "machine learning", "generative ai", "llm", "gpt",
            "neural", "deep learning", "artificial intelligence", 
            "agents", "openai", "langchain", "rag", "embedding",
            "llama", "gemini", "claude", "chatgpt", "stable diffusion",
            "transformer", "token", "model", "ai/ml", "mlops"
        ]
    },
    "cn": {
        "name": "InfoQ 中文",
        "url": "https://www.infoq.cn/feed",
        "lang": "cn",
        "icon": "🌏",
        "ai_keywords": [
            "人工智能", "机器学习", "生成式AI", "大语言模型", "LLM",
            "神经网络", "深度学习", "AI", "Agent", "智能体",
            "OpenAI", "ChatGPT", "GPT", "langchain", "RAG",
            "Embedding", "Gemini", "Claude", "Llama", "扩散模型",
            "Transformer", "MLOps", "AI Agent", "大模型"
        ]
    },
    "verge": {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "lang": "en",
        "icon": "📰",
        "ai_keywords": [
            "ai", "artificial intelligence", "machine learning", "chatgpt",
            "openai", "google deepmind", "anthropic", "llm", "gpt",
            "neural", "robotics", "automation", "generative"
        ]
    },
    "ars": {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "lang": "en",
        "icon": "🔧",
        "ai_keywords": [
            "ai", "artificial intelligence", "machine learning", "chatgpt",
            "openai", "llm", "gpt", "neural network", "deep learning",
            "google deepmind", "anthropic", "stable diffusion"
        ]
    },
    "tc": {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "lang": "en",
        "icon": "💰",
        "ai_keywords": [
            "ai", "artificial intelligence", "machine learning", "chatgpt",
            "openai", "llm", "generative ai", "startup", "funding",
            "anthropic", "foundation model", "ai startup"
        ]
    },
    "wired": {
        "name": "Wired",
        "url": "https://www.wired.com/feed/rss",
        "lang": "en",
        "icon": "🔌",
        "ai_keywords": [
            "ai", "artificial intelligence", "machine learning", "chatgpt",
            "openai", "llm", "generative ai", "neural", "deepmind"
        ]
    },
    "hn": {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/rss",
        "lang": "en",
        "icon": "👨‍💻",
        "ai_keywords": [
            "ai", "machine learning", "llm", "gpt", "openai", "chatgpt",
            "language model", "neural", "deep learning", "transformer",
            "anthropic", "claude", "gemini", "mistral", "rAG"
        ]
    },
    "tns": {
        "name": "The New Stack",
        "url": "https://thenewstack.io/feed/",
        "lang": "en",
        "icon": "☁️",
        "ai_keywords": [
            "ai", "machine learning", "llm", "kubernetes", "cloud native",
            "devops", "openai", "generative ai", "mlops", "agent"
        ]
    },
    "vb": {
        "name": "VentureBeat",
        "url": "https://feeds.feedburner.com/venturebeat/SZYF",
        "lang": "en",
        "icon": "📊",
        "ai_keywords": [
            "ai", "artificial intelligence", "machine learning", "chatgpt",
            "openai", "llm", "generative ai", "enterprise ai", "ai model"
        ]
    },
    "devto": {
        "name": "dev.to",
        "url": "https://dev.to/feed",
        "lang": "en",
        "icon": "🧑‍💻",
        "ai_keywords": [
            "ai", "machine learning", "llm", "gpt", "openai", "chatgpt",
            "python", "langchain", "rag", "embedding", "neural network",
            "tensorflow", "pytorch", "generative ai", "llama"
        ]
    },
    "mit_tr": {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "lang": "en",
        "icon": "🔬",
        "ai_keywords": [
            "ai", "machine learning", "llm", "gpt", "openai", "neural",
            "artificial intelligence", "generative", "model", "deep learning",
            "algorithm", "robot", "computer vision", "nlp", "chip", "quantum"
        ]
    },
    "theregister": {
        "name": "The Register",
        "url": "https://www.theregister.com/headlines.atom",
        "lang": "en",
        "icon": "🗞️",
        "ai_keywords": [
            "ai", "machine learning", "llm", "gpt", "openai", "chatgpt",
            "nvidia", "amd", "intel", "cloud", "kubernetes", "python",
            "linux", "security", "cyber", "data", "neural", "software"
        ]
    },
    "nvidia_blog": {
        "name": "NVIDIA Blog",
        "url": "https://blogs.nvidia.com/feed/",
        "lang": "en",
        "icon": "🟢",
        "ai_keywords": [
            "ai", "machine learning", "gpu", "llm", "cuda", "neural",
            "deep learning", "generative", "model", "inference", "training"
        ]
    },
    "ai_news": {
        "name": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "lang": "en",
        "icon": "🤖",
        "ai_keywords": [
            "ai", "machine learning", "llm", "gpt", "artificial intelligence",
            "generative", "neural", "deep learning", "nlp", "automation"
        ]
    },
}

AI_NEWS_SOURCE_ORDER = [
    "en",
    "cn",
    "mit_tr",
    "theregister",
    "nvidia_blog",
    "ai_news",
    "verge",
    "ars",
    "tc",
    "wired",
    "hn",
    "tns",
    "vb",
    "devto",
]

def is_ai_related(title, description, keywords):
    """Check if content is AI-related based on keywords."""
    text = f"{title} {description}".lower()
    return any(kw.lower() in text for kw in keywords)

def _atom_ns(tag: str) -> str:
    return f"{{http://www.w3.org/2005/Atom}}{tag}"

def fetch_source(source_id, config, days_ago=0):
    """Fetch and filter news from a single source."""
    try:
        req = urllib.request.Request(config["url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode('utf-8')
        
        root = ET.fromstring(content)
        items = root.findall('.//item') or root.findall('.//entry') or []
        
        results = []
        
        for item in items:
            title = (
                (item.findtext('title') or '').strip()
                or (item.findtext(_atom_ns('title')) or '').strip()
            )
            link = (item.findtext('link') or '').strip()
            if not link:
                for ln in item.findall(_atom_ns('link')):
                    href = (ln.get('href') or '').strip()
                    if href:
                        link = href
                        break
            
            # Try different date field names
            pub_date_str = (
                item.findtext('pubDate') or 
                item.findtext('published') or 
                item.findtext('updated') or 
                item.findtext(_atom_ns('published')) or
                item.findtext(_atom_ns('updated')) or
                ''
            ).strip()
            
            description = (
                (item.findtext('description') or item.findtext('summary') or item.findtext('content') or '').strip()
                or (item.findtext(_atom_ns('summary')) or '').strip()
            )
            # Clean HTML from description
            description = html.unescape(description) if description else ''
            description = re.sub(r"<[^>]+>", "", description)
            description = description[:500] + "..." if len(description) > 500 else description
            
            # Parse date
            pub_date = None
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %Z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S%z',
                '%a, %d %b %Y %H:%M:%S',
            ]
            for fmt in date_formats:
                try:
                    pub_date = datetime.strptime(pub_date_str[:25], fmt)
                    break
                except Exception:
                    pass
            
            if not item_in_date_window(pub_date, days_ago):
                continue
            
            # Filter by AI keywords
            if is_ai_related(title, description, config["ai_keywords"]):
                results.append({
                    'title': html.unescape(title) if isinstance(title, str) else title,
                    'link': link,
                    'date': pub_date,
                    'description': description,
                    'source': source_id,
                    'source_name': config["name"]
                })
        
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "results": results, "count": len(results)}
        
    except urllib.error.HTTPError as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": f"HTTP {e.code}", "results": [], "count": 0}
    except Exception as e:
        return {"source": source_id, "name": config["name"], "icon": config["icon"], "error": str(e), "results": [], "count": 0}

def format_output(source_results, filter_sites=None):
    """Format all results into readable output."""
    output = []
    total = 0
    
    order = AI_NEWS_SOURCE_ORDER
    
    for source_id in order:
        if filter_sites and source_id not in filter_sites:
            continue
            
        result = source_results.get(source_id)
        if not result or result["count"] == 0:
            continue
            
        icon = result["icon"]
        name = result["name"]
        items = result["results"]
        
        if "error" in result:
            output.append(f"{icon} **{name}** · ❌ {result['error']}")
            output.append("")
            continue
        
        total += len(items)
        output.extend(
            format_source_block(
                icon, f"{name}（{len(items)} 条）", items, max_items=10, desc_max=160
            )
        )
        output.append("")
    
    if total == 0:
        return "今日无AI相关新资讯。"
    
    header = f"📈 **AI / 技术资讯** · 共 {total} 条\n"
    return header + "\n".join(output).rstrip()

if __name__ == "__main__":
    argv, cli_cap = parse_argv_max_sources(sys.argv[1:])
    max_cap = resolve_max_sources(cli_cap)
    days = 0
    filter_sites = {"en", "cn"}  # Default: InfoQ only
    
    if len(argv) > 0:
        if argv[0].isdigit():
            days = int(argv[0])
    
    if len(argv) > 1:
        raw_filter = argv[1]
        if raw_filter == "all":
            filter_sites = set(SOURCES.keys())
        else:
            filter_sites = set(raw_filter.replace(" ", "").split(","))
    
    order_keys = [k for k in AI_NEWS_SOURCE_ORDER if k in filter_sites]
    order_keys = apply_source_cap(order_keys, max_cap)
    
    results = {}
    for source_id in order_keys:
        results[source_id] = fetch_source(source_id, SOURCES[source_id], days)
    
    out = format_output(results, filter_sites)
    if max_cap is not None:
        out = f"（本 run 抓取 {len(order_keys)} 个源，上限 {max_cap}）\n\n" + out
    print(out)
