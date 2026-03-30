---
name: world-news
description: Fetch major world news from authoritative international sources. Triggers when user asks to "get world news", "international news summary", "汇总国际资讯", "fetch major news", "世界新闻", "国内外大事件", "经济新闻", "军事新闻", "科技新闻", "中国相关新闻", or any request to retrieve news about world affairs, politics, economy, military, technology from sites like BBC, NY Times, Reuters, SCMP, Financial Times, The Verge, Ars Technica, Wired, TechCrunch, etc.
---

# World News Skill

Fetch major world news from multiple authoritative international sources via RSS feeds.

## Supported Sources

### 🌍 International / World News
| Code | Name | Language |
|------|------|----------|
| BBC News | BBC World | English |
| NY Times World | New York Times World | English |
| SCMP | South China Morning Post | English |
| Reuters | Reuters World News | English |
| The Guardian | The Guardian World | English |
| Al Jazeera | Al Jazeera English | English |
| NPR | NPR News | English |
| The Independent | The Independent World | English |
| France 24 | France 24 | English |
| Sky News | Sky News World | English |

### 💹 Economy / Finance
| Code | Name | Language |
|------|------|----------|
| BBC Business | BBC Business | English |
| NY Times Business | New York Times Business | English |
| Financial Times | FT | English |
| The Economist | The Economist World This Week | English |
| TechCrunch | TechCrunch | English |

### 📱 Technology
| Code | Name | Language |
|------|------|----------|
| The Verge | The Verge | English |
| Ars Technica | Ars Technica | English |
| Wired | Wired | English |
| The New Stack | The New Stack | English |
| TechCrunch | TechCrunch | English |

## Usage

```bash
python3 <path>/fetch_news.py [days_ago] [category]
```

**Parameters:**
- `days_ago`: Rolling window in days. **`0` = calendar today only** (items must have a parseable pub date ≥ today 00:00 local; undated items are dropped). Use `1` or higher for multi-day windows.
- `category`: all, world, economy, tech, china (default: all)
- **Source cap**: `export OPENCLAW_NEWS_MAX_SOURCES=10` or append `--max-sources 10` (fetches only the first N sources in the built-in priority order).

**Examples:**
```bash
# Today's all news
python3 fetch_news.py

# Last 3 days of world news
python3 fetch_news.py 3 world

# Last 7 days of tech news
python3 fetch_news.py 7 tech

# Today's economy news
python3 fetch_news.py 0 economy

# China-related news from international sources
python3 fetch_news.py 3 china
```

## Script Location

```
~/.openclaw/skills/world-news/scripts/fetch_news.py
```

## Output Format

每条：**摘要**、**发布时间**、**原文链接**；按来源分块。

## Trigger Phrases

- "世界新闻"
- "国际资讯"
- "国内外大事件"
- "经济新闻"
- "军事新闻"
- "科技新闻"
- "中国相关新闻"
- "汇总国际资讯"
- "get world news"
- "international news"
- "major news events"

## Note

Chinese domestic news sources have limited RSS availability due to anti-scraping measures. This skill uses international sources (BBC, NY Times, SCMP, Reuters, etc.) to provide China-related and world news coverage.
