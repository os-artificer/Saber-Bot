#!/usr/bin/env bash
# Unified global news (bash)；由 fetch_global_news.sh 在 Python 失败时调用。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../shared/bash_lib/news_rss_common.sh
source "$SCRIPT_DIR/../../shared/bash_lib/news_rss_common.sh"

need_cmd curl jq date
command -v grep >/dev/null 2>&1 || die "需要 grep"

parse_args() {
  local days="$DEFAULT_NEWS_LOOKBACK_DAYS"
  local category="all"
  local -a raw=()
  mapfile -t raw < <(parse_argv_max_sources "$@")
  local cap=""
  local -a args=()
  local hit=0
  local line
  for line in "${raw[@]}"; do
    if [[ "$line" == "--CAP--" ]]; then hit=1; continue; fi
    if [[ $hit -eq 1 ]]; then cap="$line"; hit=0; continue; fi
    args+=("$line")
  done
  if [[ ${#args[@]} -gt 0 ]]; then
    if [[ "${args[0]}" =~ ^[0-9]+$ ]]; then
      days="${args[0]}"
    else
      category="$(echo "${args[0]}" | tr '[:upper:]' '[:lower:]')"
    fi
  fi
  if [[ ${#args[@]} -gt 1 ]]; then
    if [[ "${args[1]}" =~ ^[0-9]+$ ]]; then
      days="${args[1]}"
    else
      category="$(echo "${args[1]}" | tr '[:upper:]' '[:lower:]')"
    fi
  fi
  if [[ "$category" == "intl" || "$category" == "international" ]]; then
    category="world"
  fi
  local resolved_cap
  resolved_cap="$(resolve_max_sources "$cap")"
  echo "$days"
  echo "$category"
  echo "${resolved_cap:-}"
}

# --- source metadata (parallel to Python) ---
declare -A SRC_NAME SRC_KIND SRC_ICON SRC_BUCKET SRC_TAGS
declare -A SRC_URL SRC_SINA_LID

SRC_NAME[xinhua_world]="新华网·国际"
SRC_KIND[xinhua_world]="rss"
SRC_URL[xinhua_world]="http://www.xinhuanet.com/world/news_world.xml"
SRC_ICON[xinhua_world]="🌐"
SRC_BUCKET[xinhua_world]="china"
SRC_TAGS[xinhua_world]="all,world,geopolitics"

SRC_NAME[xinhua_politics]="新华网·时政"
SRC_KIND[xinhua_politics]="rss"
SRC_URL[xinhua_politics]="http://www.xinhuanet.com/politics/news_politics.xml"
SRC_ICON[xinhua_politics]="🏛️"
SRC_BUCKET[xinhua_politics]="china"
SRC_TAGS[xinhua_politics]="all,domestic,politics,geopolitics"

SRC_NAME[xinhua_fortune]="新华网·财经"
SRC_KIND[xinhua_fortune]="rss"
SRC_URL[xinhua_fortune]="http://www.xinhuanet.com/fortune/news_fortune.xml"
SRC_ICON[xinhua_fortune]="💹"
SRC_BUCKET[xinhua_fortune]="china"
SRC_TAGS[xinhua_fortune]="all,economy,domestic"

SRC_NAME[cns_scroll]="中新网·滚动"
SRC_KIND[cns_scroll]="rss"
SRC_URL[cns_scroll]="https://www.chinanews.com.cn/rss/scroll-news.xml"
SRC_ICON[cns_scroll]="📰"
SRC_BUCKET[cns_scroll]="china"
SRC_TAGS[cns_scroll]="all,domestic,world,economy,geopolitics,war,politics"

SRC_NAME[huanqiu_cn]="环球时报（中文）"
SRC_KIND[huanqiu_cn]="rss"
SRC_URL[huanqiu_cn]="https://m.huanqiu.com/rss"
SRC_ICON[huanqiu_cn]="🌏"
SRC_BUCKET[huanqiu_cn]="china"
SRC_TAGS[huanqiu_cn]="all,domestic,world,politics,geopolitics"

SRC_NAME[huanqiu_gt]="环球时报 Global Times"
SRC_KIND[huanqiu_gt]="rss"
SRC_URL[huanqiu_gt]="https://www.globaltimes.cn/rss/outbrain.xml"
SRC_ICON[huanqiu_gt]="🗞️"
SRC_BUCKET[huanqiu_gt]="china"
SRC_TAGS[huanqiu_gt]="all,world,china,geopolitics,war,politics"

SRC_NAME[people_politics]="人民网·政治"
SRC_KIND[people_politics]="rss"
SRC_URL[people_politics]="http://www.people.com.cn/rss/politics.xml"
SRC_ICON[people_politics]="🏛️"
SRC_BUCKET[people_politics]="china"
SRC_TAGS[people_politics]="all,domestic,politics,geopolitics"

SRC_NAME[ftchinese]="FT中文网"
SRC_KIND[ftchinese]="rss"
SRC_URL[ftchinese]="https://www.ftchinese.com/rss/feed"
SRC_ICON[ftchinese]="💼"
SRC_BUCKET[ftchinese]="china"
SRC_TAGS[ftchinese]="all,world,economy,domestic"

SRC_NAME[bbc_cn]="BBC中文网"
SRC_KIND[bbc_cn]="rss"
SRC_URL[bbc_cn]="https://feeds.bbci.co.uk/zhongwen/simp/rss.xml"
SRC_ICON[bbc_cn]="🇬🇧"
SRC_BUCKET[bbc_cn]="china"
SRC_TAGS[bbc_cn]="all,world,economy,geopolitics,war,politics"

SRC_NAME[scmp_cn]="南华早报"
SRC_KIND[scmp_cn]="rss"
SRC_URL[scmp_cn]="https://www.scmp.com/rss/world.xml"
SRC_ICON[scmp_cn]="🇭🇰"
SRC_BUCKET[scmp_cn]="china"
SRC_TAGS[scmp_cn]="all,world,economy,geopolitics,war"

SRC_NAME[sina_domestic]="新浪国内"
SRC_KIND[sina_domestic]="sina"
SRC_SINA_LID[sina_domestic]="2516"
SRC_ICON[sina_domestic]="🇨🇳"
SRC_BUCKET[sina_domestic]="china"
SRC_TAGS[sina_domestic]="all,domestic,politics,economy,geopolitics"

SRC_NAME[sina_world]="新浪国际"
SRC_KIND[sina_world]="sina"
SRC_SINA_LID[sina_world]="2517"
SRC_ICON[sina_world]="🌐"
SRC_BUCKET[sina_world]="china"
SRC_TAGS[sina_world]="all,world,geopolitics,war"

SRC_NAME[sina_economy]="新浪财经"
SRC_KIND[sina_economy]="sina"
SRC_SINA_LID[sina_economy]="1686"
SRC_ICON[sina_economy]="💹"
SRC_BUCKET[sina_economy]="china"
SRC_TAGS[sina_economy]="all,economy,domestic"

SRC_NAME[sina_mil]="新浪军事"
SRC_KIND[sina_mil]="sina"
SRC_SINA_LID[sina_mil]="2425"
SRC_ICON[sina_mil]="⚔️"
SRC_BUCKET[sina_mil]="china"
SRC_TAGS[sina_mil]="all,war,geopolitics,domestic"

SRC_NAME[sina_tech]="新浪科技"
SRC_KIND[sina_tech]="sina"
SRC_SINA_LID[sina_tech]="1195"
SRC_ICON[sina_tech]="📱"
SRC_BUCKET[sina_tech]="china"
SRC_TAGS[sina_tech]="all,tech,economy"

SRC_NAME[bbc_world]="BBC News"
SRC_KIND[bbc_world]="rss"
SRC_URL[bbc_world]="https://feeds.bbci.co.uk/news/world/rss.xml"
SRC_ICON[bbc_world]="🇬🇧"
SRC_BUCKET[bbc_world]="world"
SRC_TAGS[bbc_world]="all,world,china"

SRC_NAME[nytimes_world]="NY Times World"
SRC_KIND[nytimes_world]="rss"
SRC_URL[nytimes_world]="https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
SRC_ICON[nytimes_world]="🇺🇸"
SRC_BUCKET[nytimes_world]="world"
SRC_TAGS[nytimes_world]="all,world,china"

SRC_NAME[reuters_world]="Reuters"
SRC_KIND[reuters_world]="rss"
SRC_URL[reuters_world]="https://feeds.reuters.com/reuters/worldnews"
SRC_ICON[reuters_world]="📰"
SRC_BUCKET[reuters_world]="world"
SRC_TAGS[reuters_world]="all,world"

SRC_NAME[bbc_business]="BBC Business"
SRC_KIND[bbc_business]="rss"
SRC_URL[bbc_business]="https://feeds.bbci.co.uk/news/business/rss.xml"
SRC_ICON[bbc_business]="💷"
SRC_BUCKET[bbc_business]="world"
SRC_TAGS[bbc_business]="all,economy"

SRC_NAME[ft]="Financial Times"
SRC_KIND[ft]="rss"
SRC_URL[ft]="https://www.ft.com/rss/home"
SRC_ICON[ft]="💹"
SRC_BUCKET[ft]="world"
SRC_TAGS[ft]="all,economy"

SRC_NAME[theverge]="The Verge"
SRC_KIND[theverge]="rss"
SRC_URL[theverge]="https://www.theverge.com/rss/index.xml"
SRC_ICON[theverge]="📱"
SRC_BUCKET[theverge]="world"
SRC_TAGS[theverge]="all,tech"

SRC_NAME[arstechnica]="Ars Technica"
SRC_KIND[arstechnica]="rss"
SRC_URL[arstechnica]="https://feeds.arstechnica.com/arstechnica/index"
SRC_ICON[arstechnica]="🔧"
SRC_BUCKET[arstechnica]="world"
SRC_TAGS[arstechnica]="all,tech"

SRC_NAME[wired]="Wired"
SRC_KIND[wired]="rss"
SRC_URL[wired]="https://www.wired.com/feed/rss"
SRC_ICON[wired]="🔌"
SRC_BUCKET[wired]="world"
SRC_TAGS[wired]="all,tech"

FETCH_ORDER=(
  xinhua_politics xinhua_fortune xinhua_world cns_scroll huanqiu_cn huanqiu_gt
  people_politics ftchinese sina_domestic sina_world sina_economy sina_mil sina_tech
  bbc_cn scmp_cn bbc_world nytimes_world reuters_world bbc_business ft
  theverge arstechnica wired
)

CAT_NAMES_all="📋 全部资讯"
CAT_NAMES_domestic="🇨🇳 国内动态"
CAT_NAMES_world="🌐 国际局势"
CAT_NAMES_economy="💹 经济财经"
CAT_NAMES_geopolitics="🌍 地缘政治"
CAT_NAMES_war="⚔️ 战争军事"
CAT_NAMES_politics="🏛️ 政治要闻"
CAT_NAMES_tech="📱 科技数码"
CAT_NAMES_security="🔐 安全资讯"
CAT_NAMES_china="🇨🇳 中国相关"

source_matches() {
  local tags="$1"
  local category="$2"
  [[ "$category" == "all" ]] && return 0
  [[ ",$tags," == *",$category,"* ]]
}

should_show_world_bucket() {
  local c="$1"
  [[ "$c" == "all" || "$c" == "world" || "$c" == "economy" || "$c" == "tech" || "$c" == "china" ]]
}

main() {
  local -a pa=()
  mapfile -t pa < <(parse_args "$@")
  local days="${pa[0]}"
  local category="${pa[1]}"
  local cap="${pa[2]:-}"

  local supported="all domestic world economy geopolitics war politics tech security china"
  [[ " $supported " == *" $category "* ]] || {
    echo "Unsupported category: $category" >&2
    echo "Supported: $(echo "$supported" | tr ' ' ',')" >&2
    exit 2
  }

  local -a selected=()
  local sid
  for sid in "${FETCH_ORDER[@]}"; do
    source_matches "${SRC_TAGS[$sid]:-}" "$category" || continue
    selected+=("$sid")
  done
  mapfile -t selected < <(apply_source_cap "$cap" "${selected[@]}")

  local -a china_blocks=() world_blocks=()
  local fetch_out
  for sid in "${selected[@]}"; do
    fetch_out=""
    if [[ "${SRC_KIND[$sid]}" == "sina" ]]; then
      fetch_out="$(fetch_sina "${SRC_NAME[$sid]}" "${SRC_ICON[$sid]}" "${SRC_SINA_LID[$sid]}" "$days" || true)"
    else
      fetch_out="$(fetch_rss "${SRC_NAME[$sid]}" "${SRC_ICON[$sid]}" "${SRC_URL[$sid]}" "$days" || true)"
    fi
    if [[ "${SRC_BUCKET[$sid]}" == "china" ]]; then
      china_blocks+=("$fetch_out")
    else
      world_blocks+=("$fetch_out")
    fi
  done

  local cat_title="📋 全部资讯"
  eval "cat_title=\"\${CAT_NAMES_${category}:-📋 全部资讯}\""
  local head_line
  head_line="${cat_title} $(date +%m-%d)"

  local china_body world_body
  china_body=""
  world_body=""
  [[ ${#china_blocks[@]} -gt 0 ]] && china_body="$(format_section_from_blocks "## 🇨🇳 国内与中文源" "${china_blocks[@]}")"
  if should_show_world_bucket "$category" && [[ ${#world_blocks[@]} -gt 0 ]]; then
    world_body="$(format_section_from_blocks "## 🌍 国际主流源" "${world_blocks[@]}")"
  fi

  local out=""
  out="$head_line"
  if [[ -n "$china_body" ]]; then
    out+=$'\n\n'"$china_body"
  fi
  if [[ -n "$world_body" ]]; then
    out+=$'\n\n'"$world_body"
  fi
  out="$(echo -n "$out" | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}')"
  [[ -z "$(echo "$out" | tr -d '[:space:]')" ]] && out="📭 暂无相关资讯"
  if [[ -z "$out" ]]; then out="📭 暂无相关资讯"; fi
  if [[ "$out" != "📭 暂无相关资讯" && -z "$(echo "$out" | tr -d '[:space:]')" ]]; then out="📭 暂无相关资讯"; fi

  if [[ -n "$cap" ]]; then
    out="（本 run 抓取 ${#selected[@]} 个源，上限 ${cap}）"$'\n\n'"$out"
  fi

  local appendix_on="${OPENCLAW_GLOBAL_NEWS_URL_APPENDIX:-1}"
  appendix_on="$(echo "$appendix_on" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  if [[ "$appendix_on" != "0" && "$appendix_on" != "false" && "$appendix_on" != "no" && "$appendix_on" != "off" && "$out" != "📭 暂无相关资讯" ]]; then
    local max_u=300
    local raw_max="${OPENCLAW_GLOBAL_NEWS_URL_APPENDIX_MAX:-}"
    raw_max="$(echo -n "$raw_max" | tr -d '[:space:]')"
    if [[ "$raw_max" =~ ^[0-9]+$ ]]; then
      max_u="$raw_max"
      [[ "$max_u" -lt 1 ]] && max_u=1
      [[ "$max_u" -gt 2000 ]] && max_u=2000
    fi
    local -a all_b=("${china_blocks[@]}" "${world_blocks[@]}")
    mapfile -t url_lines < <(collect_urls_from_blocks "$max_u" "${all_b[@]}")
    local appendix
    appendix="$(format_url_appendix_block "${url_lines[@]}")"
    out+="$appendix"
  fi

  printf '%s\n' "$out"
}

main "$@"
