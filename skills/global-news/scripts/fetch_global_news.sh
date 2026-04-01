#!/usr/bin/env bash
# 统一入口：优先 python3 fetch_global_news.py；失败或不可用时回退 fetch_global_news.bash.sh
# 用法与 Python 脚本一致： [days_ago] [category] [--max-sources N]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/fetch_global_news.py"
BASH_IMPL="$SCRIPT_DIR/fetch_global_news.bash.sh"

if command -v python3 >/dev/null 2>&1 && [[ -f "$PY" ]]; then
  python3 "$PY" "$@" && exit 0
fi
exec bash "$BASH_IMPL" "$@"
