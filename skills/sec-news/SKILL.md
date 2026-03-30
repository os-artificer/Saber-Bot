---
name: sec-news
description: Fetch cybersecurity news including network penetration testing, latest vulnerabilities (CVEs), attack techniques, and social engineering articles. Triggers when user asks to "get security news", "latest CVE vulnerabilities", "penetration testing news", "社会工程学文章", "网络安全资讯", "漏洞信息", "attack techniques", "pentest news", or any request about cybersecurity, ethical hacking, vulnerability research, social engineering, or offensive security.
---

# Security News & Penetration Testing Skill

Fetch cybersecurity news from multiple authoritative sources: security news, vulnerabilities/CVEs, attack techniques, and social engineering.

## Supported Categories

### 🎯 Security News
| Icon | Source | Description |
|------|--------|-------------|
| 🎯 | The Hacker News | 全球最权威网络安全媒体 |
| 💻 | BleepingComputer | 知名网络安全新闻站 |
| 📰 | SecurityWeek | 企业安全新闻 |
| 🔍 | Krebs on Security | Brian Krebs独立调查 |
| 🌑 | Dark Reading | 企业安全分析 |
| ⚠️ | Threatpost | 独立网络安全新闻 |
| 🕵️ | Naked Security | Sophos安全研究 |
| 🔐 | Help Net Security | 网络安全新闻与研究 |
| 🛡️ | Schneier on Security | Bruce Schneier专家博客 |
| 📡 | SANS ISC Diary | 互联网风暴中心日记 |
| 🕸️ | Kaspersky Securelist | 卡巴斯基威胁研究 |
| 🦠 | ESET WeLiveSecurity | ESET 安全资讯 |
| ⚡ | Rapid7 Blog | 漏洞与检测研究 |
| 🔮 | Recorded Future | 威胁情报与网络风险 |

### 💉 Vulnerabilities / CVE
| Icon | Source | Description |
|------|--------|-------------|
| 🕵️ | Tenable Blog | 漏洞研究与分析 |
| 🏆 | Qualys Blog | Qualys漏洞研究 |
| 💉 | Exploit-DB | 漏洞利用代码数据库 |
| 🦅 | Palo Alto Unit 42 | 高级威胁研究 |

### 🎭 Social Engineering
| Icon | Source | Description |
|------|--------|-------------|
| 🎭 | Social-Engineer.org | 社会工程学权威资源 |
| ✅ | TrustedSec | 渗透测试与社会工程 |
| ⚔️ | Offensive Security | 渗透测试培训与研究 |

### 🛠️ Security Tools / Threat Intel
| Icon | Source | Description |
|------|--------|-------------|
| 🦅 | CrowdStrike | 端点安全与威胁情报 |
| 1️⃣ | SentinelOne | AI端点保护 |
| 🔥 | Mandiant | APT威胁研究 |
| 🏢 | CSO Online | 企业安全战略 |

## Usage

```bash
python3 <path>/fetch_sec_news.py [days_ago] [category]
```

**Parameters:**
- `days_ago`: Rolling window (default: 7). Items without a parseable pub date are dropped. **`0` = today only** (local midnight onward).
- `category`: all, vulns, attacks, se, tools (default: all)
- **Source cap**: `OPENCLAW_NEWS_MAX_SOURCES=N` or `--max-sources N`.

**Examples:**
```bash
# All security news from last 7 days
python3 fetch_sec_news.py

# Last 30 days of all security news
python3 fetch_sec_news.py 30

# Vulnerability/CVE news only
python3 fetch_sec_news.py 14 vulns

# Social engineering articles
python3 fetch_sec_news.py 30 se

# Attack techniques / security news
python3 fetch_sec_news.py 7 attacks

# Security tools / threat intel
python3 fetch_sec_news.py 7 tools
```

## Script Location

```
~/.openclaw/skills/sec-news/scripts/fetch_sec_news.py
```

## Trigger Phrases

- "网络安全资讯"
- "最新漏洞"
- "CVE信息"
- "渗透测试新闻"
- "社会工程学"
- "社工文章"
- "攻击手段"
- "安全新闻"
- "get security news"
- "latest vulnerabilities"
- "pentest news"
- "social engineering articles"
