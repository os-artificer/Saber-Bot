#!/usr/bin/env bash
#
# 一键将 Saber-Bot/skills 安装到 OpenClaw（~/.openclaw/skills）并启用 skills.entries
#
# 用法:
#   ./scripts/install-openclaw-skills.sh
#   ./scripts/install-openclaw-skills.sh --link          # 符号链接到本仓库（开发时改 skill 立即生效）
#   ./scripts/install-openclaw-skills.sh --dry-run
#   OPENCLAW_HOME=/path ./scripts/install-openclaw-skills.sh
#
# 环境变量:
#   OPENCLAW_HOME   默认 ~/.openclaw
#   OPENCLAW_SKILLS 默认 $OPENCLAW_HOME/skills
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILLS_SRC="${REPO_ROOT}/skills"
PATCH_JSON="${SCRIPT_DIR}/patch-openclaw-skills-json.py"

OPENCLAW_HOME="${OPENCLAW_HOME:-${HOME}/.openclaw}"
OPENCLAW_SKILLS="${OPENCLAW_SKILLS:-${OPENCLAW_HOME}/skills}"
OPENCLAW_JSON="${OPENCLAW_HOME}/openclaw.json"

# 与 skills/ 下目录一致（不含 shared，shared 为脚本依赖库）
SKILL_NAMES=(
  china-news
  dev-news
  infoq-ai-news
  sec-news
  world-news
  weather
)

DRY_RUN=0
USE_LINK=0
DO_JSON=1

usage() {
  sed -n '1,20p' "$0" | tail -n +2
  echo "Options:"
  echo "  -h, --help       显示帮助"
  echo "  -n, --dry-run    只打印将要执行的操作"
  echo "  -l, --link       使用符号链接（否则 rsync 复制）"
  echo "  --no-json        不修改 openclaw.json"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -n|--dry-run) DRY_RUN=1; shift ;;
    -l|--link) USE_LINK=1; shift ;;
    --no-json) DO_JSON=0; shift ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -d "${SKILLS_SRC}" ]]; then
  echo "ERROR: skills source not found: ${SKILLS_SRC}" >&2
  exit 1
fi

log() { echo "[install-openclaw-skills] $*"; }

run() {
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

mkdir_p() {
  run "mkdir -p \"$1\""
}

if [[ "${USE_LINK}" -eq 1 ]]; then
  mkdir_p "${OPENCLAW_SKILLS}"
  for name in "${SKILL_NAMES[@]}"; do
    src="${SKILLS_SRC}/${name}"
    dst="${OPENCLAW_SKILLS}/${name}"
    if [[ ! -e "${src}" ]]; then
      log "WARN: skip missing ${src}"
      continue
    fi
    run "rm -rf \"${dst}\""
    run "ln -sfn \"${src}\" \"${dst}\""
  done
  if [[ -d "${SKILLS_SRC}/shared" ]]; then
    run "rm -rf \"${OPENCLAW_SKILLS}/shared\""
    run "ln -sfn \"${SKILLS_SRC}/shared\" \"${OPENCLAW_SKILLS}/shared\""
  fi
else
  mkdir_p "${OPENCLAW_SKILLS}"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo "[dry-run] rsync -a ${SKILLS_SRC}/ ${OPENCLAW_SKILLS}/"
  else
    rsync -a "${SKILLS_SRC}/" "${OPENCLAW_SKILLS}/"
  fi
fi

if [[ "${DO_JSON}" -eq 1 ]]; then
  if [[ ! -f "${PATCH_JSON}" ]]; then
    echo "ERROR: missing ${PATCH_JSON}" >&2
    exit 1
  fi
  if [[ ! -f "${OPENCLAW_JSON}" ]]; then
    log "WARN: ${OPENCLAW_JSON} not found — skip JSON patch（请先配置 OpenClaw 或设置 OPENCLAW_HOME）"
  else
    args=("${OPENCLAW_JSON}" "${SKILL_NAMES[@]}")
    if [[ "${DRY_RUN}" -eq 1 ]]; then
      echo "[dry-run] python3 \"${PATCH_JSON}\" ${args[*]}"
    else
      python3 "${PATCH_JSON}" "${args[@]}"
    fi
  fi
fi

log "Done. Skills root: ${OPENCLAW_SKILLS}"
if command -v openclaw >/dev/null 2>&1; then
  log "Tip: 若 Gateway 已加载 skill 缓存，可执行: openclaw gateway restart"
fi
