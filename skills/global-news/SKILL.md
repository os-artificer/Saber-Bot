---
name: global-news
description: |
  全球/国内/国际新闻。触发词：新闻、全球资讯、国际资讯、时政、突发、中东、要闻等。
  【硬性约束·违反视为错误输出】
  (1) 运行 fetch_global_news.py（Python 3）后，对用户可见的回复中 MUST 保留脚本 stdout 里每一个含 https:// 或 http:// 的完整行；NEVER 删除、省略、改写、概括掉任何 URL 字符串。
  (2) NEVER 用自编的「突发/中东局势/国内要闻/国际其他」等分栏卡片替代脚本原文；该行为会剥掉全部链接。
  (3) 文末「原文链接汇总」块 MUST 原样转发；若只能分段发送，最后一段 MUST 包含该汇总块。
  (4) NEVER 输出「点击链接查看详情」若消息中不存在至少一行以 https:// 开头的明文 URL。
  脚本路径：~/.openclaw/skills/global-news/scripts/fetch_global_news.py
---

# Global News Skill

## 模型约束（最高优先级，先于一切文风与排版）

以下规则**优先于**摘要、分类、emoji 卡片、字数压缩。违反即**错误回复**。

| 必须（MUST） | 禁止（MUST NOT） |
|----------------|------------------|
| 执行 `fetch_global_news.py` 后，把**终端打印的完整文本**发给用户（可拆多条消息） | 把脚本输出**改写**成「突发 / 中东 / 国内要闻」等**自编专题**，再只写要点不要链接 |
| **保留**输出中**每一个**以 `https://` 或 `http://` 开头的**完整行**（含文末「原文链接汇总」每一行） | **删除、合并、概括**掉任何 URL 行，或把 URL 改成「见官网」「点此」等无地址表述 |
| 若必须缩写：只删**无 URL 的说明句**，**不得**删任何含 `://` 的行 | 写「共约 N 条，点击链接查看」却不附带**至少一行**明文 `https://` |
| 分段发送时：**最后一段**须含**原文链接汇总**整块（或完整脚本输出） | 仅发送归纳标题而无 URL |

**自检（发出前在心里核对）：** 用户能否用 Ctrl+F 在消息里搜到 **`https://`**？若不能，**禁止发送**，应改为粘贴脚本原文或仅发链接汇总块。

统一入口抓取国内与国际资讯，覆盖政务央媒、国内门户、**环球时报（中/英）**、**人民网政治**、**FT中文网**、**中新网**滚动、国际中文媒体与主流英文媒体。

（安全垂直类 FreeBuf 等已归 **`tech-rss-news` → `fetch_sec_news.py`**，避免与综合新闻重复。）

## 使用方法

**唯一入口**为同目录下的 **`fetch_global_news.py`**，用 **Python 3** 运行（不依赖 Bash/shell 包装脚本，便于 Windows / macOS / Linux 一致使用）。

```text
python3 ~/.openclaw/skills/global-news/scripts/fetch_global_news.py [天数] [分类] [--max-sources N]
```

- **跨平台**：类 Unix 一般用 `python3`；Windows 若未配置 `python3`，可用 `py -3` 或 `python`（须为 Python 3）。
- **Python 路径**：依赖 `skills/shared` 下的模块（与仓库布局一致时可直接运行）。

参数：

- `天数`：回溯天数（默认 `3`，约过去 **72 小时**内，滚动窗口；`0` = 仅今天）
- `分类`：`all | domestic | world | economy | geopolitics | war | politics | tech | security | china`
- 抓取源数量上限（可选）：`--max-sources N` 或 `--max-sources=N`，会转发给底层新闻脚本

示例：

```text
python3 fetch_global_news.py
python3 fetch_global_news.py 3 world
python3 fetch_global_news.py 7 tech
python3 fetch_global_news.py 0 domestic
python3 fetch_global_news.py 3 china
```

## 分类说明

- `all`：国内+国际全量
- `world / economy / tech`：同时聚合国内中文国际源与世界主流英文源
- `domestic / geopolitics / war / politics / security`：以国内综合源为主
- `china`：国际媒体中的中国相关新闻

## 输出格式

每条资讯包含：**优先一行裸 `https://` 链接**（便于 IM 识别可点击）、摘要、时间、**`[阅读原文](url)`**（Markdown 可点击）、`链接 ·` 行与再次重复的裸 URL；输出分为「国内与中文源」和「境外主流源」两块（按分类自动显示）。

## 给 Agent 的硬性规则（不可省略）

1. **禁止**用自编的「突发 / 中东局势 / 国内要闻 / 国际其他」等专题卡片**替换**脚本输出；那种版式会丢掉全部 `https://` 链接。
2. 用户要全球/国内/国际资讯时，**必须**运行 `fetch_global_news.py`，将**脚本打印的原文**（含每条 `https://` 与 `[阅读原文](…)`）发给用户；可分段发送，**不可**只发归纳标题。
3. **禁止**出现「点击链接查看详情」却**没有任何 URL** 的句子。
4. 若篇幅过长只能压缩，**每条仍须保留至少一行以 `https://` 开头的完整原文链接**。
5. 脚本末尾自带 **「原文链接汇总」** 纯文本块（每行一个 `https://`）；**必须一并转发**，勿省略。
6. **字符串级约束**：对用户最终可见文本做任意编辑时，**不得**减少 `https://` 与 `http://` 子串的出现次数（与脚本 stdout 相比）；若会减少，则**不得编辑**，改为原样转发或只发链接汇总段。

## 为何聊天里没有链接？（排错）

| 现象 | 更可能原因 |
|------|------------|
| 正文是「突发/中东/国内要闻」分栏，**没有**「中新网」「新华网」等媒体名 | **模型**在归纳脚本，未粘贴原始输出，链接被删光。 |
| 终端里脚本文末有 `https://`，QQ 里看不到 | **QQ 渠道**或插件对富文本/长消息做了过滤（较少见）；可试发一条纯 `https://www.example.com` 验证。 |
| 终端里就没有 `https://` | **Skill 未更新**或跑错脚本；或 `OPENCLAW_GLOBAL_NEWS_URL_APPENDIX=0` 关掉了文末汇总。 |

## 文末「原文链接汇总」

- 默认开启；每行一个 URL，纯文本，便于复制。
- 关闭：`OPENCLAW_GLOBAL_NEWS_URL_APPENDIX=0`
- 条数上限：`OPENCLAW_GLOBAL_NEWS_URL_APPENDIX_MAX`（默认 300，最大 2000）
