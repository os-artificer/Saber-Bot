"""
AI / Tech RSS source configuration.
"""

from __future__ import annotations

from typing import Any, Dict, List

SOURCES: Dict[str, Dict[str, Any]] = {
    "en": {"name": "InfoQ English", "url": "https://www.infoq.com/feed", "lang": "en", "icon": "🌐", "region": "overseas", "ai_keywords": ["ai", "machine learning", "generative ai", "llm", "gpt", "neural", "deep learning", "artificial intelligence", "agents", "openai", "langchain", "rag", "embedding", "llama", "gemini", "claude", "chatgpt", "stable diffusion", "transformer", "token", "model", "ai/ml", "mlops"]},
    "cn": {"name": "InfoQ 中文", "url": "https://www.infoq.cn/feed", "lang": "cn", "icon": "🌏", "region": "china", "ai_keywords": ["人工智能", "机器学习", "生成式AI", "大语言模型", "LLM", "神经网络", "深度学习", "AI", "Agent", "智能体", "OpenAI", "ChatGPT", "GPT", "langchain", "RAG", "Embedding", "Gemini", "Claude", "Llama", "扩散模型", "Transformer", "MLOps", "AI Agent", "大模型"]},
    "verge": {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "lang": "en", "icon": "📰", "region": "overseas", "ai_keywords": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "google deepmind", "anthropic", "llm", "gpt", "neural", "robotics", "automation", "generative"]},
    "ars": {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "lang": "en", "icon": "🔧", "region": "overseas", "ai_keywords": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "llm", "gpt", "neural network", "deep learning", "google deepmind", "anthropic", "stable diffusion"]},
    "tc": {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "lang": "en", "icon": "💰", "region": "overseas", "ai_keywords": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "llm", "generative ai", "startup", "funding", "anthropic", "foundation model", "ai startup"]},
    "wired": {"name": "Wired", "url": "https://www.wired.com/feed/rss", "lang": "en", "icon": "🔌", "region": "overseas", "ai_keywords": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "llm", "generative ai", "neural", "deepmind"]},
    "hn": {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "lang": "en", "icon": "👨‍💻", "region": "overseas", "ai_keywords": ["ai", "machine learning", "llm", "gpt", "openai", "chatgpt", "language model", "neural", "deep learning", "transformer", "anthropic", "claude", "gemini", "mistral", "rAG"]},
    "tns": {"name": "The New Stack", "url": "https://thenewstack.io/feed/", "lang": "en", "icon": "☁️", "region": "overseas", "ai_keywords": ["ai", "machine learning", "llm", "kubernetes", "cloud native", "devops", "openai", "generative ai", "mlops", "agent"]},
    "vb": {"name": "VentureBeat", "url": "https://feeds.feedburner.com/venturebeat/SZYF", "lang": "en", "icon": "📊", "region": "overseas", "ai_keywords": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "llm", "generative ai", "enterprise ai", "ai model"]},
    "devto": {"name": "dev.to", "url": "https://dev.to/feed", "lang": "en", "icon": "🧑‍💻", "region": "overseas", "ai_keywords": ["ai", "machine learning", "llm", "gpt", "openai", "chatgpt", "python", "langchain", "rag", "embedding", "neural network", "tensorflow", "pytorch", "generative ai", "llama"]},
    "mit_tr": {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "lang": "en", "icon": "🔬", "region": "overseas", "ai_keywords": ["ai", "machine learning", "llm", "gpt", "openai", "neural", "artificial intelligence", "generative", "model", "deep learning", "algorithm", "robot", "computer vision", "nlp", "chip", "quantum"]},
    "theregister": {"name": "The Register", "url": "https://www.theregister.com/headlines.atom", "lang": "en", "icon": "🗞️", "region": "overseas", "ai_keywords": ["ai", "machine learning", "llm", "gpt", "openai", "chatgpt", "nvidia", "amd", "intel", "cloud", "kubernetes", "python", "linux", "security", "cyber", "data", "neural", "software"]},
    "nvidia_blog": {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/", "lang": "en", "icon": "🟢", "region": "overseas", "ai_keywords": ["ai", "machine learning", "gpu", "llm", "cuda", "neural", "deep learning", "generative", "model", "inference", "training"]},
    "ai_news": {"name": "AI News", "url": "https://www.artificialintelligence-news.com/feed/", "lang": "en", "icon": "🤖", "region": "overseas", "ai_keywords": ["ai", "machine learning", "llm", "gpt", "artificial intelligence", "generative", "neural", "deep learning", "nlp", "automation"]},
    "huggingface": {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "lang": "en", "icon": "🤗", "region": "overseas", "accept_all": True, "ai_keywords": []},
    "qbitai": {"name": "量子位", "url": "https://www.qbitai.com/feed", "lang": "cn", "icon": "⚛️", "region": "china", "accept_all": True, "ai_keywords": []},
}

AI_NEWS_SOURCE_ORDER: List[str] = [
    "en",
    "cn",
    "qbitai",
    "huggingface",
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

AI_REGION_ORDER: Dict[str, List[str]] = {
    "china": [sid for sid in AI_NEWS_SOURCE_ORDER if SOURCES.get(sid, {}).get("region") == "china"],
    "overseas": [sid for sid in AI_NEWS_SOURCE_ORDER if SOURCES.get(sid, {}).get("region") == "overseas"],
}
