---
name: dev-news
description: Fetch programming language version logs, features, organization info, and open source product news. Triggers when user asks to "get programming language news", "编程语言版本", "开源产品动态", "开发技术新闻", "最新编程语言特性", "开源工具更新", "developer news", or any request about programming languages (Python/Rust/Go/TypeScript etc.) version updates, language features, OSS product releases, or developer community updates.
---

# Dev News Skill

Fetch programming language news, version logs, features, and open source product updates.

## Supported Programming Languages

| Icon | Language | Organization | Description |
|------|----------|--------------|-------------|
| 🐍 | Python | Python Software Foundation | 通用编程语言，数据科学/AI首选 |
| 🦀 | Rust | Rust Foundation | 系统编程，内存安全 |
| 📘 | TypeScript | Microsoft | JavaScript超集，静态类型 |
| 🟢 | Node.js | OpenJS Foundation | JavaScript运行时 |
| 🔵 | Go | Google | Google开发的编译型语言 |
| ☕ | Java | Oracle/OpenJDK | 企业级后端开发 |
| 🟣 | Kotlin | JetBrains/Google | JVM语言，Android首选 |
| 💜 | C# | Microsoft | .NET平台主语言 |
| 🍎 | Swift | Apple | iOS/macOS开发语言 |
| 💎 | Ruby | Ruby Association | 简洁web开发语言 |

## Supported Open Source Products

| Icon | Product | Description |
|------|---------|-------------|
| 🐙 | GitHub Blog | 全球最大代码托管平台动态 |
| 🐳 | Docker | 容器化技术 |
| ☸️ | Kubernetes | 容器编排平台 |
| 🌱 | Spring | Java企业级框架 |
| ⚛️ | React | UI构建库 |
| 💚 | Vue.js | 渐进式前端框架 |
| 📐 | Angular | Google前端框架 |
| 🦕 | Deno | 安全 JS/TS 运行时 |
| 🔥 | Svelte | 编译型前端框架 |
| 🐧 | Linux | 开源内核 |
| 📎 | VS Code | 微软轻量级编辑器 |
| 🐘 | PostgreSQL | 开源关系型数据库 |

## Developer Community

| Icon | Source | Description |
|------|--------|-------------|
| 👨‍💻 | dev.to | 开发者社区博客 |
| 👾 | Hacker News | YC程序员社区 |
| 🦞 | Lobsters | 技术社区 |

## Usage

```bash
python3 <path>/fetch_dev_news.py [days_ago] [category]
```

**Parameters:**
- `days_ago`: Rolling window (default: 7). Undated entries are dropped. **`0` = today only**.
- `category`: all, languages, oss, devtools (default: all)
- **Source cap**: `OPENCLAW_NEWS_MAX_SOURCES=N` or `--max-sources N`.

**Examples:**
```bash
# All dev news from last 7 days
python3 fetch_dev_news.py

# Programming language news only, last 7 days
python3 fetch_dev_news.py 7 languages

# Open source tools updates, last 14 days
python3 fetch_dev_news.py 14 oss

# Developer community news
python3 fetch_dev_news.py 7 devtools
```

## Script Location

```
~/.openclaw/skills/dev-news/scripts/fetch_dev_news.py
```

## Trigger Phrases

- "编程语言版本"
- "最新编程语言特性"
- "开源产品动态"
- "开发技术新闻"
- "Python/Go/Rust最新消息"
- "developer news"
- "编程语言新闻"
- "开源工具更新"
