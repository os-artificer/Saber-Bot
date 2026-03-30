---
name: weather
description: "查询天气、气温、降雨与预报（支持中英文地点）。通过 wttr.in（主）或 Open-Meteo（备）获取实时与多日预报，无需 API Key。在用户询问天气、气温、是否下雨、周末/明天天气、某城市气候时使用。"
homepage: https://wttr.in/:help
metadata:
  {
    "openclaw":
      {
        "emoji": "☔",
        "requires": { "bins": ["curl"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "curl",
              "bins": ["curl"],
              "label": "Install curl (brew)",
            },
          ],
      },
  }
---

# Weather（天气）

使用 `curl` 获取天气，不依赖 API Key。

## 何时使用

- 「北京今天天气」「上海明天会下雨吗」
- 「What's the weather in Tokyo?」「London forecast」
- 出行前查看气温、风力、湿度

## 地点

将城市名或机场 IATA 编码进行 URL 编码后写入 URL（空格用 `+` 或 `%20`）。

## 主路径：wttr.in

```bash
# 一行摘要（示例：上海）
curl -s --max-time 15 "wttr.in/Shanghai?format=3"

# 当前详情
curl -s --max-time 20 "wttr.in/Shanghai?0"

# 多日预报（文本）
curl -s --max-time 25 "wttr.in/Shanghai"

# JSON（便于解析）
curl -s --max-time 20 "wttr.in/Shanghai?format=j1"
```

常用 `format`：`%l` 地点、`%c` 状况、`%t` 气温、`%f` 体感、`%w` 风、`%h` 湿度、`%p` 降水。

## 备用：Open-Meteo（wttr 不可用或需结构化数据时）

先地理编码再预报（将 `NAME` 换成城市英文名或拼音，一般可解析中国地名）：

```bash
curl -s --max-time 15 "https://geocoding-api.open-meteo.com/v1/search?name=Shanghai&count=1"
```

从返回中取 `latitude`、`longitude`，再请求：

```bash
curl -s --max-time 20 "https://api.open-meteo.com/v1/forecast?latitude=31.22&longitude=121.49&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto&forecast_days=7"
```

## 注意

- 适度请求，避免短时间内大量 `curl`。
- 极端天气预警、航空气象等请以官方发布为准。
- **中国境内**：暴雨、台风、寒潮等预警与停课停运信息，请以**中央气象台**（[weather.cma.cn](https://weather.cma.cn)）及**当地气象、应急部门**发布为准；本 skill 为通用预报，不替代政务预警。
