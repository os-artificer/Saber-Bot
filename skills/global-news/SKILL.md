---
name: global-news
description: 获取国内与国际综合资讯的统一技能，覆盖国内权威源、中文国际源与主流英文国际源。用户提到新闻、世界新闻、国际资讯、国内新闻、地缘政治、经济、科技、战争、时政时触发。
---

# Global News Skill

统一入口抓取国内与国际资讯，覆盖政务央媒、国内门户、国际中文媒体与主流英文媒体。

## 使用方法

```bash
python3 ~/.openclaw/skills/global-news/scripts/fetch_global_news.py [天数] [分类]
```

参数：

- `天数`：回溯天数（默认 `0` = 仅今天）
- `分类`：`all | domestic | world | economy | geopolitics | war | politics | tech | security | china`
- 抓取源数量上限（可选）：`--max-sources N` 或 `--max-sources=N`，会转发给底层新闻脚本

示例：

```bash
# 今日国内+国际综合资讯
python3 fetch_global_news.py

# 近3天国际局势（中文源 + 国际主流源）
python3 fetch_global_news.py 3 world

# 近7天科技
python3 fetch_global_news.py 7 tech

# 国内动态（国内源）
python3 fetch_global_news.py 0 domestic

# 国际媒体里的中国相关新闻
python3 fetch_global_news.py 3 china
```

## 分类说明

- `all`：国内+国际全量
- `world / economy / tech`：同时聚合国内中文国际源与世界主流英文源
- `domestic / geopolitics / war / politics / security`：以国内综合源为主
- `china`：国际媒体中的中国相关新闻

## 输出格式

每条资讯包含：摘要、发布时间、原文链接；输出分为「国内与中文源」和「国际主流源」两块（按分类自动显示）。
