---
name: tech-rss-news
description: |
  IT 技术 RSS：AI 资讯、开发/开源、安全/CVE。触发：AI 新闻、编程语言、CVE、网络安全、InfoQ、dev.to 等。
  【硬性约束】运行 fetch_ai_news.py / fetch_dev_news.py / fetch_sec_news.py（Python 3）后，对用户回复 MUST 保留脚本输出中每一个 https:// 或 http:// 完整 URL；NEVER 删除或概括掉链接行；NEVER 用无 URL 的 bullet 列表替代脚本全文；文末「原文链接汇总」MUST 原样转发。若需缩写，仅删除无 URL 的句子，不得减少 URL 条数。
  脚本目录：~/.openclaw/skills/tech-rss-news/scripts/
---

# Tech RSS News（技术 RSS 聚合）

## 模型约束（最高优先级）

- **MUST NOT** 删除、合并或省略任何含 `https://`、`http://` 的行（含 `链接 ·`、`[阅读原文](url)`、文末裸 URL）。
- **MUST NOT** 将脚本输出改写成「精选 / 要点」列表而不带 URL。
- **MUST** 需要缩写时：只删无链接的句子；**MUST** 保证用户仍能用搜索找到与脚本等量的 URL 子串（或原样分段转发 stdout）。

本技能提供三条独立 **Python** 脚本，共用 `skills/shared` 下的格式化与过滤模块；数据源已抽离为公共配置文件，并统一使用 `china`（中国境内）/`overseas`（境外）划分。**不使用** `.sh` / Bash 入口，以保证 Windows / macOS / Linux 行为一致。

## 统一入口（仅 Python 3）

直接调用对应 `.py` 文件：

```text
python3 ~/.openclaw/skills/tech-rss-news/scripts/fetch_ai_news.py [days_ago] [site_filter]
python3 ~/.openclaw/skills/tech-rss-news/scripts/fetch_dev_news.py [days_ago] [category]
python3 ~/.openclaw/skills/tech-rss-news/scripts/fetch_sec_news.py [days_ago] [category]
```

- **跨平台**：类 Unix 用 `python3`；Windows 可用 `py -3` 或 `python`（须为 Python 3）。
- **依赖**：标准库 + `skills/shared`；需能访问各 RSS / JSON 端点（安全脚本会拉 NVD gzip、CISA JSON 等）。

## 1. AI / Tech（`fetch_ai_news.py`）

含：InfoQ EN/CN、主流媒体、**Hugging Face Blog**、**量子位**（中文 AI 垂直媒体；机器之心官方 RSS 当前返回 HTML，故用量子位替代）、MIT TR、NVIDIA Blog 等。

**NVD JSON**：部分网络环境对 `nvd.nist.gov` 返回 403，可设置环境变量 `OPENCLAW_NVD_CVE_GZ_URL` 指向可访问的 `nvdcve-1.1-recent.json.gz` 镜像地址。（主要用于 **sec** 脚本中的 NVD 源。）

```text
python3 <path>/fetch_ai_news.py [days_ago] [site_filter]
```

- `days_ago`：默认 **`3`**（约过去 **72 小时**，滚动窗口）；**`0` = 仅今天**
- `site_filter`：站点 code 逗号分隔或 `all`（默认 `en,cn`）
- 源上限：`OPENCLAW_NEWS_MAX_SOURCES=N` 或 `--max-sources N`

输出与 **global-news** 一致：**每条**含优先一行裸 `https://`、`[阅读原文](url)`、`链接 ·` 与重复裸 URL；三条脚本均在文末输出 **「原文链接汇总」**（每行一个 URL，纯文本）。

环境变量：`OPENCLAW_TECH_RSS_URL_APPENDIX`（默认开启，`0`/`false` 关闭）、`OPENCLAW_TECH_RSS_URL_APPENDIX_MAX`（默认 300，最大 2000）。

**重要（转发给用户前）**：若对脚本输出做二次摘要或改写，**须保留每条新闻对应的原文链接**，勿改成无链接的条目列表。

**字符串级约束**：对用户可见文本的编辑**不得**减少脚本 stdout 中 `https://` / `http://` 出现次数；否则应原样转发脚本输出。

## 2. Dev（`fetch_dev_news.py`）

含：编程语言官方博客；GitHub/Docker/K8s 等开源产品；**Product Hunt**、**InfoQ 聚合 feed**、**The New Stack**、**OSCHINA**；社区 **dev.to**、**HN 首页 / Show**、**36氪**、Lobsters。

```text
python3 <path>/fetch_dev_news.py [days_ago] [category]
```

- `category`：`all` \| `languages` \| `oss` \| `devtools`（默认 `all`）
- `days_ago`：默认 **`3`**（约 **72 小时**）；**`0` = 仅今天**
- 每条新闻为完整 **【n】+ 链接块**（与 AI/安全脚本同级的 IM 可点击格式），文末有 **原文链接汇总**。

## 3. Security（`fetch_sec_news.py`）

- **漏洞与 CVE**：**NVD**（`nvdcve-1.1-recent.json.gz`）、**CISA KEV**（JSON）、安全厂商博客、Exploit-DB、**安全客**、**FreeBuf**、**绿盟科技博客**
- **威胁情报**：Krebs、Schneier、SANS ISC（全文 RSS）、Recorded Future 等（见 `skills/shared/tech_rss_sec_sources.py`）
- **社会工程 / 工具**：`se`、`tools` 分类

```text
python3 <path>/fetch_sec_news.py [days_ago] [category]
```

- `category`：`all` \| `vulns` \| `attacks` \| `se` \| `tools`（默认 `all`）
- `days_ago`：默认 **`3`**（约 **72 小时**）；**`0` = 仅今天**
- 每条为 **im_clickable** 链接格式，文末 **原文链接汇总**。

## 脚本路径（安装后）

```text
~/.openclaw/skills/tech-rss-news/scripts/fetch_ai_news.py
~/.openclaw/skills/tech-rss-news/scripts/fetch_dev_news.py
~/.openclaw/skills/tech-rss-news/scripts/fetch_sec_news.py
```

## 触发短语（节选）

- AI：`AI 资讯`、`大模型`、`Hugging Face`、`量子位`
- Dev：`开源发布`、`Product Hunt`、`OSCHINA`、`36氪`、`HN Show`
- Sec：`CVE`、`NVD`、`CISA`、`漏洞`、`FreeBuf`、`安全客`
