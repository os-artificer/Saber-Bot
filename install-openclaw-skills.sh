#!/usr/bin/env bash
# 便捷入口：等价于 ./scripts/install-openclaw-skills.sh
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/install-openclaw-skills.sh" "$@"
