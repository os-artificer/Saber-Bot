#!/usr/bin/env bash
# Bash 回退：编程语言 / 开源 / 开发者社区（与 fetch_dev_news.py 同源列表与分区）。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../shared/bash_lib/news_rss_common.sh
source "$SCRIPT_DIR/../../shared/bash_lib/news_rss_common.sh"

need_cmd curl jq date
command -v grep >/dev/null 2>&1 || die "需要 grep"

declare -A D_NAME D_URL D_ICON D_ORG D_DESC D_GROUP

# --- LANG (group=lang) ---
_register() { local k="$1" g="$2" n="$3" u="$4" i="$5" o="$6" d="$7"
  D_NAME[$k]="$n"; D_URL[$k]="$u"; D_ICON[$k]="$i"; D_ORG[$k]="$o"; D_DESC[$k]="$d"; D_GROUP[$k]="$g"
}
_register python lang "Python" "https://blog.python.org/feeds/posts/default" "🐍" "Python Software Foundation" "通用编程语言，数据科学/AI首选"
_register rust lang "Rust" "https://blog.rust-lang.org/feed.xml" "🦀" "Rust Foundation" "系统编程语言，主打内存安全"
_register typescript lang "TypeScript" "https://devblogs.microsoft.com/typescript/feed/" "📘" "Microsoft" "JavaScript超集，静态类型"
_register nodejs lang "Node.js" "https://nodejs.org/en/feed/blog.xml" "🟢" "OpenJS Foundation" "JavaScript运行时"
_register golang lang "Go" "https://go.dev/blog/index.xml" "🔵" "Google" "Google开发的编译型语言"
_register java lang "Java" "https://www.oracle.com/java/technologies/javadoc-and-docs.html" "☕" "Oracle / OpenJDK" "企业级后端开发"
_register kotlin lang "Kotlin" "https://blog.jetbrains.com/kotlin/feed/" "🟣" "JetBrains / Google" "JVM语言，Android首选"
_register csharp lang "C#" "https://devblogs.microsoft.com/dotnet/feed/" "💜" "Microsoft" ".NET平台主语言"
_register swift lang "Swift" "https://swift.org/blog/swift-5.9-released/" "🍎" "Apple" "iOS/macOS开发语言"
_register ruby lang "Ruby" "https://ruby.social/@RubyWeekly/feed" "💎" "Ruby Association" "简洁web开发语言"

# --- OSS (group=oss) ---
_register github oss "GitHub Blog" "https://github.com/blog.atom" "🐙" "" "全球最大代码托管平台动态"
_register producthunt oss "Product Hunt" "https://www.producthunt.com/feed" "🚀" "" "新产品与工具发布"
_register infoq_feed oss "InfoQ（聚合 feed）" "https://feed.infoq.com/" "📚" "" "InfoQ 英文站聚合 RSS"
_register thenewstack oss "The New Stack" "https://thenewstack.io/feed/" "☁️" "" "云原生与基础设施"
_register oschina oss "OSCHINA" "https://www.oschina.net/news/rss" "🐼" "" "中文开源技术资讯"
_register docker oss "Docker Blog" "https://blog.docker.com/feed/" "🐳" "" "容器化技术领导者"
_register kubernetes oss "Kubernetes" "https://kubernetes.io/feed.xml" "☸️" "" "容器编排平台"
_register spring oss "Spring" "https://spring.io/blog.atom" "🌱" "" "Java企业级框架"
_register react oss "React" "https://react.dev/blog/rss.xml" "⚛️" "" "UI构建库"
_register vue oss "Vue.js" "https://blog.vuejs.org/feed.xml" "💚" "" "渐进式前端框架"
_register deno oss "Deno" "https://deno.com/blog/rss.xml" "🦕" "" "安全 JS/TS 运行时"
_register svelte oss "Svelte" "https://svelte.dev/blog/rss.xml" "🔥" "" "编译型前端框架"
_register angular oss "Angular" "https://blog.angular.io/feed.atom" "📐" "" "Google前端框架"
_register linux oss "Linux" "https://lkml.org/lkml/recent.xml" "🐧" "" "开源内核"
_register vscode oss "VS Code" "https://code.visualstudio.com/feed.xml" "📎" "" "微软轻量级编辑器"
_register postgresql oss "PostgreSQL" "https://www.postgresql.org/blogs/rss/" "🐘" "" "开源关系型数据库"

# --- COMM (group=comm) ---
_register devto comm "dev.to" "https://dev.to/feed" "👨‍💻" "" "开发者社区博客"
_register hackernews comm "Hacker News（首页）" "https://hnrss.org/frontpage" "👾" "" "HN 热门（hnrss frontpage）"
_register hn_show comm "Hacker News（Show）" "https://hnrss.org/show" "🎬" "" "HN Show 分区"
_register kr36 comm "36氪" "https://36kr.com/feed" "⚡" "" "科技与创业热点"
_register lobsters comm "Lobsters" "https://lobste.rs/rss" "🦞" "" "技术社区"

DEV_LANG_ORDER=(python rust typescript nodejs golang java kotlin csharp swift ruby)
DEV_OSS_ORDER=(github producthunt infoq_feed thenewstack oschina docker kubernetes spring react vue angular deno svelte linux vscode postgresql)
DEV_COMM_ORDER=(devto hackernews hn_show kr36 lobsters)

dev_fetch_order() {
  local category="$1"
  local -a out=()
  local k x
  if [[ "$category" == "languages" ]]; then
    for k in "${DEV_LANG_ORDER[@]}"; do out+=("$k"); done
  elif [[ "$category" == "oss" ]]; then
    for k in "${DEV_OSS_ORDER[@]}"; do out+=("$k"); done
  elif [[ "$category" == "devtools" ]]; then
    for k in "${DEV_COMM_ORDER[@]}"; do out+=("$k"); done
  else
    local seen=""
    for x in "${DEV_LANG_ORDER[@]}" "${DEV_OSS_ORDER[@]}" "${DEV_COMM_ORDER[@]}"; do
      [[ "$seen" == *"|$x|"* ]] && continue
      seen+="|$x|"
      out+=("$x")
    done
  fi
  printf '%s\n' "${out[@]}"
}

parse_dev_args() {
  local -a raw=()
  mapfile -t raw < <(parse_argv_max_sources "$@")
  local cap="" hit=0 line
  local -a args=()
  for line in "${raw[@]}"; do
    if [[ "$line" == "--CAP--" ]]; then hit=1; continue; fi
    if [[ $hit -eq 1 ]]; then cap="$line"; hit=0; continue; fi
    args+=("$line")
  done
  local days="$DEFAULT_NEWS_LOOKBACK_DAYS"
  local category="all"
  [[ ${#args[@]} -gt 0 ]] && [[ "${args[0]}" =~ ^[0-9]+$ ]] && days="${args[0]}"
  if [[ ${#args[@]} -gt 0 ]] && ! [[ "${args[0]}" =~ ^[0-9]+$ ]]; then
    category="$(echo "${args[0]}" | tr '[:upper:]' '[:lower:]')"
  fi
  if [[ ${#args[@]} -gt 1 ]]; then
    if [[ "${args[1]}" =~ ^[0-9]+$ ]]; then
      days="${args[1]}"
    else
      category="$(echo "${args[1]}" | tr '[:upper:]' '[:lower:]')"
    fi
  fi
  local resolved
  resolved="$(resolve_max_sources "$cap")"
  echo "$days"
  echo "$category"
  echo "${resolved:-}"
}

dev_emit_source() {
  local sid="$1" block="$2" maxn="$3"
  local cnt name icon org desc
  cnt="$(echo "$block" | grep -c '^ITEM:' || true)"
  [[ "${cnt:-0}" -eq 0 ]] && return 0
  name="${D_NAME[$sid]:-}"
  icon="${D_ICON[$sid]:-}"
  org="${D_ORG[$sid]:-}"
  desc="${D_DESC[$sid]:-}"
  local g="${D_GROUP[$sid]:-}"
  echo ""
  echo ""
  if [[ "$g" == "lang" ]]; then
    echo "$icon **$name** — $org"
    echo "   📝 $desc"
  else
    echo "$icon **$name** — $desc"
  fi
  local idx=1
  local line raw title link ep d
  while IFS= read -r line; do
    [[ "$line" == ITEM:* ]] || continue
    [[ $idx -gt $maxn ]] && break
    raw="${line#ITEM:}"
    IFS=$'\x1e' read -r title link ep d <<<"$raw"
    echo ""
    echo "$RULE"
    mapfile -t _bl < <(format_news_item_lines "$idx" "$title" "$d" "$ep" "$link" 480)
    local _ln
    for _ln in "${_bl[@]}"; do echo "$_ln"; done
    idx=$((idx + 1))
  done <<<"$(echo "$block" | grep '^ITEM:')"
}

main() {
  local -a pa=()
  mapfile -t pa < <(parse_dev_args "$@")
  local days="${pa[0]}"
  local category="${pa[1]}"
  local cap="${pa[2]:-}"

  local -a order=()
  mapfile -t order < <(dev_fetch_order "$category")
  mapfile -t order < <(apply_source_cap "$cap" "${order[@]}")

  declare -A BLOCKS=()
  local sid fetch_out
  for sid in "${order[@]}"; do
    fetch_out="$(fetch_rss "${D_NAME[$sid]}" "${D_ICON[$sid]}" "${D_URL[$sid]}" "$days" || true)"
    BLOCKS["$sid"]="$fetch_out"
  done

  local total=0
  for sid in "${order[@]}"; do
    total=$((total + $(echo "${BLOCKS[$sid]}" | grep -c '^ITEM:' || true)))
  done

  local out=""
  out="# 💻 编程语言 & 开源动态（近${days}天）"$'\n'
  out+="📊 共获取 ${total} 条更新"$'\n'

  if [[ "$category" == "languages" ]]; then
    out+=$'\n'"### 🐍 编程语言动态"
    for sid in "${DEV_LANG_ORDER[@]}"; do
      [[ -n "${BLOCKS[$sid]:-}" ]] || continue
      out+="$(dev_emit_source "$sid" "${BLOCKS[$sid]}" 3)"
    done
  elif [[ "$category" == "oss" ]]; then
    out+=$'\n'"### 🛠️ 开源产品/工具动态"
    for sid in "${DEV_OSS_ORDER[@]}"; do
      [[ -n "${BLOCKS[$sid]:-}" ]] || continue
      out+="$(dev_emit_source "$sid" "${BLOCKS[$sid]}" 3)"
    done
  elif [[ "$category" == "devtools" ]]; then
    out+=$'\n'"### 👨‍💻 开发者社区热点"
    for sid in "${DEV_COMM_ORDER[@]}"; do
      [[ -n "${BLOCKS[$sid]:-}" ]] || continue
      out+="$(dev_emit_source "$sid" "${BLOCKS[$sid]}" 5)"
    done
  else
    out+=$'\n'"### 🐍 编程语言动态"
    for sid in "${DEV_LANG_ORDER[@]}"; do
      [[ -n "${BLOCKS[$sid]:-}" ]] || continue
      out+="$(dev_emit_source "$sid" "${BLOCKS[$sid]}" 3)"
    done
    out+=$'\n'"### 🛠️ 开源产品/工具动态"
    for sid in "${DEV_OSS_ORDER[@]}"; do
      [[ -n "${BLOCKS[$sid]:-}" ]] || continue
      out+="$(dev_emit_source "$sid" "${BLOCKS[$sid]}" 3)"
    done
    out+=$'\n'"### 👨‍💻 开发者社区热点"
    for sid in "${DEV_COMM_ORDER[@]}"; do
      [[ -n "${BLOCKS[$sid]:-}" ]] || continue
      out+="$(dev_emit_source "$sid" "${BLOCKS[$sid]}" 5)"
    done
  fi

  if [[ -n "$cap" ]]; then
    out="（本 run 抓取 ${#order[@]} 个源，上限 ${cap}）"$'\n\n'"$out"
  fi

  local appendix_on="${OPENCLAW_TECH_RSS_URL_APPENDIX:-1}"
  appendix_on="$(echo "$appendix_on" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  if [[ "$appendix_on" != "0" && "$appendix_on" != "false" && "$appendix_on" != "no" && "$appendix_on" != "off" && "$total" -gt 0 ]]; then
    local max_u=300
    local raw_max="${OPENCLAW_TECH_RSS_URL_APPENDIX_MAX:-}"
    raw_max="$(echo -n "$raw_max" | tr -d '[:space:]')"
    if [[ "$raw_max" =~ ^[0-9]+$ ]]; then
      max_u="$raw_max"
      [[ "$max_u" -lt 1 ]] && max_u=1
      [[ "$max_u" -gt 2000 ]] && max_u=2000
    fi
    local -a blks=()
    for sid in "${order[@]}"; do blks+=("${BLOCKS[$sid]}"); done
    mapfile -t url_lines < <(collect_urls_from_blocks "$max_u" "${blks[@]}")
    out+="$(format_url_appendix_block "${url_lines[@]}")"
  fi

  printf '%s\n' "$out"
}

main "$@"
