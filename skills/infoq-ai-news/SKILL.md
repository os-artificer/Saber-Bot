---
name: infoq-ai-news
description: Fetch and summarize AI/Tech news from multiple authoritative IT news sources via RSS feeds. Triggers when user asks to "get AI news", "tech news summary", "汇总AI资讯", "fetch news from multiple sources", "get latest AI updates", "IT资讯", or any request to retrieve AI/ML/technology news from sites like InfoQ, The Verge, Ars Technica, TechCrunch, Wired, Hacker News, The New Stack, VentureBeat, or dev.to.
---

# Multi-Source AI/Tech News Skill

Fetch AI/Tech news from multiple authoritative sources using RSS feeds.

## Supported Sources

| Code | Name | URL | Language |
|------|------|-----|----------|
| `en` | InfoQ English | infoq.com | English |
| `cn` | InfoQ 中文 | infoq.cn | Chinese |
| `verge` | The Verge | theverge.com | English |
| `ars` | Ars Technica | arstechnica.com | English |
| `tc` | TechCrunch | techcrunch.com | English |
| `wired` | Wired | wired.com | English |
| `hn` | Hacker News | news.ycombinator.com | English |
| `tns` | The New Stack | thenewstack.io | English |
| `vb` | VentureBeat | venturebeat.com | English |
| `devto` | dev.to | dev.to | English |
| `mit_tr` | MIT Technology Review | technologyreview.com | English |
| `theregister` | The Register | theregister.com | English |
| `nvidia_blog` | NVIDIA Blog | blogs.nvidia.com | English |
| `ai_news` | AI News | artificialintelligence-news.com | English |

## Usage

```bash
python3 <path>/fetch_ai_news.py [days_ago] [site_filter]
```

**Parameters:**
- `days_ago`: Rolling window (default: **`0` = today only**, requires parseable dates). Undated items are dropped.
- `site_filter`: Comma-separated site codes or "all" (default: "en,cn")
- **Source cap**: `OPENCLAW_NEWS_MAX_SOURCES=N` or `--max-sources N` (applied after site filter, in built-in order).

**Examples:**
```bash
# Today's InfoQ AI news (both EN and CN)
python3 fetch_ai_news.py

# Last 7 days from InfoQ only
python3 fetch_ai_news.py 7 en,cn

# Last 7 days from ALL sources
python3 fetch_ai_news.py 7 all

# Last 3 days from specific sources
python3 fetch_ai_news.py 3 verge,ars,wired,tns

# MIT TR + Register + NVIDIA（需写入 site_filter）
python3 fetch_ai_news.py 3 mit_tr,theregister,nvidia_blog

# Today's news from Chinese site only
python3 fetch_ai_news.py 0 cn
```

## Script Location

```
~/.openclaw/skills/infoq-ai-news/scripts/fetch_ai_news.py
```

## Output Format

每条：**摘要**、**发布时间**、**原文链接**（关键词过滤后仅保留 AI/技术相关条目）。

## Trigger Phrases

- "去infoq检索当天AI资讯"
- "汇总InfoQ AI动态"
- "获取最近7天的AI新闻"
- "fetch InfoQ AI news"
- "查一下InfoQ中文站的AI新闻"
- "科技资讯"
- "AI新闻汇总"
- "IT资讯"
- "get latest AI news"
- "tech news summary"
- "帮我看看最近有什么AI新闻"
- "汇总IT资讯"
