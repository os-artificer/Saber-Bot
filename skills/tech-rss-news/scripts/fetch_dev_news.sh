#!/usr/bin/env bash
# 优先 python3 fetch_dev_news.py，失败则 fetch_dev_news.bash.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/fetch_dev_news.py"
BASH_IMPL="$SCRIPT_DIR/fetch_dev_news.bash.sh"
if command -v python3 >/dev/null 2>&1 && [[ -f "$PY" ]]; then
  python3 "$PY" "$@" && exit 0
fi
exec bash "$BASH_IMPL" "$@"
