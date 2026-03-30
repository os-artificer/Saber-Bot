# Saber-Bot

OpenClaw 自定义技能（skills）归档与一键安装。

## 一键安装到 OpenClaw

在克隆本仓库的机器上执行：

```bash
cd /path/to/Saber-Bot
./scripts/install-openclaw-skills.sh
```

或在仓库根目录使用便捷入口（等价）：

```bash
./install-openclaw-skills.sh
```

默认行为：

1. 将本仓库 `skills/` **复制**到 `~/.openclaw/skills/`（与现有文件合并，不删除你在该目录下的其它 skill）。
2. 若存在 `~/.openclaw/openclaw.json`，则为下列 skill 写入 `skills.entries.<name>.enabled: true`（并备份为 `openclaw.json.bak`）：
   - `china-news`, `dev-news`, `infoq-ai-news`, `sec-news`, `world-news`, `weather`

### 选项

| 选项 | 说明 |
|------|------|
| `-l` / `--link` | 改为**符号链接**到本仓库 `skills/`（本地改 skill 立即反映到 OpenClaw，适合开发） |
| `-n` / `--dry-run` | 只打印将要执行的命令，不写入 |
| `--no-json` | 只同步文件，**不修改** `openclaw.json` |

### 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `OPENCLAW_HOME` | `$HOME/.openclaw` | OpenClaw 配置根目录 |
| `OPENCLAW_SKILLS` | `$OPENCLAW_HOME/skills` | skill 安装目录 |

示例：

```bash
OPENCLAW_HOME=/data/saber-bot/.openclaw ./scripts/install-openclaw-skills.sh
```

### 安装后

若使用 Gateway / 常驻进程，建议重启以刷新 skill：

```bash
openclaw gateway restart
```

（未安装 `openclaw` CLI 时可忽略。）

## 仓库结构

```
skills/
  china-news/      …
  dev-news/        …
  infoq-ai-news/   …
  sec-news/        …
  world-news/      …
  weather/         …
  shared/          # 新闻脚本共用模块（news_format / news_fetch_filters）
scripts/
  install-openclaw-skills.sh
  patch-openclaw-skills-json.py
install-openclaw-skills.sh   # 根目录便捷入口 → scripts/…
```

## License

See [LICENSE](LICENSE).
