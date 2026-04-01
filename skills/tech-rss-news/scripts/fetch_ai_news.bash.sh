#!/usr/bin/env bash
# Bash 回退：AI/Tech RSS（与 fetch_ai_news.py 行为对齐，关键词为精简子集）。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../shared/bash_lib/news_rss_common.sh
source "$SCRIPT_DIR/../../shared/bash_lib/news_rss_common.sh"

need_cmd curl jq date
command -v grep >/dev/null 2>&1 || die "需要 grep"

declare -A AI_NAME AI_URL AI_ICON AI_ACCEPT AI_KWS

AI_NAME[en]="InfoQ English"
AI_URL[en]="https://www.infoq.com/feed"
AI_ICON[en]="🌐"
AI_ACCEPT[en]=0
AI_KWS[en]="ai|machine learning|generative ai|llm|gpt|openai|neural|deep learning|artificial intelligence|langchain|rag|embedding|llama|gemini|claude|chatgpt|transformer"

AI_NAME[cn]="InfoQ 中文"
AI_URL[cn]="https://www.infoq.cn/feed"
AI_ICON[cn]="🌏"
AI_ACCEPT[cn]=0
AI_KWS[cn]="人工智能|机器学习|大语言模型|llm|神经网络|深度学习|openai|chatgpt|gpt|agent|智能体|大模型|transformer"

AI_NAME[qbitai]="量子位"
AI_URL[qbitai]="https://www.qbitai.com/feed"
AI_ICON[qbitai]="⚛️"
AI_ACCEPT[qbitai]=1
AI_KWS[qbitai]=""

AI_NAME[huggingface]="Hugging Face Blog"
AI_URL[huggingface]="https://huggingface.co/blog/feed.xml"
AI_ICON[huggingface]="🤗"
AI_ACCEPT[huggingface]=1
AI_KWS[huggingface]=""

AI_NAME[mit_tr]="MIT Technology Review"
AI_URL[mit_tr]="https://www.technologyreview.com/feed/"
AI_ICON[mit_tr]="🔬"
AI_ACCEPT[mit_tr]=0
AI_KWS[mit_tr]="ai|machine learning|llm|gpt|openai|neural|artificial intelligence|generative|deep learning|nlp|robot"

AI_NAME[theregister]="The Register"
AI_URL[theregister]="https://www.theregister.com/headlines.atom"
AI_ICON[theregister]="🗞️"
AI_ACCEPT[theregister]=0
AI_KWS[theregister]="ai|machine learning|llm|gpt|openai|nvidia|kubernetes|python|linux|security|neural|software"

AI_NAME[nvidia_blog]="NVIDIA Blog"
AI_URL[nvidia_blog]="https://blogs.nvidia.com/feed/"
AI_ICON[nvidia_blog]="🟢"
AI_ACCEPT[nvidia_blog]=0
AI_KWS[nvidia_blog]="ai|machine learning|gpu|llm|cuda|neural|deep learning|generative|inference|training"

AI_NAME[ai_news]="AI News"
AI_URL[ai_news]="https://www.artificialintelligence-news.com/feed/"
AI_ICON[ai_news]="🤖"
AI_ACCEPT[ai_news]=0
AI_KWS[ai_news]="ai|machine learning|llm|gpt|artificial intelligence|generative|neural|deep learning|nlp"

AI_NAME[verge]="The Verge"
AI_URL[verge]="https://www.theverge.com/rss/index.xml"
AI_ICON[verge]="📰"
AI_ACCEPT[verge]=0
AI_KWS[verge]="ai|artificial intelligence|machine learning|chatgpt|openai|deepmind|anthropic|llm|gpt|neural|generative"

AI_NAME[ars]="Ars Technica"
AI_URL[ars]="https://feeds.arstechnica.com/arstechnica/index"
AI_ICON[ars]="🔧"
AI_ACCEPT[ars]=0
AI_KWS[ars]="ai|artificial intelligence|machine learning|chatgpt|openai|llm|gpt|neural network|deep learning|anthropic"

AI_NAME[tc]="TechCrunch"
AI_URL[tc]="https://techcrunch.com/feed/"
AI_ICON[tc]="💰"
AI_ACCEPT[tc]=0
AI_KWS[tc]="ai|artificial intelligence|machine learning|chatgpt|openai|llm|generative ai|anthropic|foundation model"

AI_NAME[wired]="Wired"
AI_URL[wired]="https://www.wired.com/feed/rss"
AI_ICON[wired]="🔌"
AI_ACCEPT[wired]=0
AI_KWS[wired]="ai|artificial intelligence|machine learning|chatgpt|openai|llm|generative ai|neural|deepmind"

AI_NAME[hn]="Hacker News"
AI_URL[hn]="https://news.ycombinator.com/rss"
AI_ICON[hn]="👨‍💻"
AI_ACCEPT[hn]=0
AI_KWS[hn]="ai|machine learning|llm|gpt|openai|chatgpt|language model|neural|deep learning|transformer|anthropic|claude|gemini"

AI_NAME[tns]="The New Stack"
AI_URL[tns]="https://thenewstack.io/feed/"
AI_ICON[tns]="☁️"
AI_ACCEPT[tns]=0
AI_KWS[tns]="ai|machine learning|llm|kubernetes|cloud native|devops|openai|generative ai|mlops|agent"

AI_NAME[vb]="VentureBeat"
AI_URL[vb]="https://feeds.feedburner.com/venturebeat/SZYF"
AI_ICON[vb]="📊"
AI_ACCEPT[vb]=0
AI_KWS[vb]="ai|artificial intelligence|machine learning|chatgpt|openai|llm|generative ai|enterprise ai"

AI_NAME[devto]="dev.to"
AI_URL[devto]="https://dev.to/feed"
AI_ICON[devto]="🧑‍💻"
AI_ACCEPT[devto]=0
AI_KWS[devto]="ai|machine learning|llm|gpt|openai|chatgpt|langchain|rag|embedding|neural|tensorflow|pytorch|generative ai|llama"

AI_NEWS_SOURCE_ORDER=(
  en cn qbitai huggingface mit_tr theregister nvidia_blog ai_news
  verge ars tc wired hn tns vb devto
)

ai_item_keep() {
  local title="$1" desc="$2" accept="$3" kws="$4"
  [[ "$accept" == "1" ]] && return 0
  local text="${title} ${desc}"
  text="${text,,}"
  local IFS='|'
  local p
  for p in $kws; do
    p="$(echo "$p" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$p" ]] && continue
    local pl="${p,,}"
    [[ "$text" == *"$pl"* ]] && return 0
  done
  return 1
}

ai_filter_block() {
  local block="$1" sid="$2"
  local accept="${AI_ACCEPT[$sid]:-0}"
  local kws="${AI_KWS[$sid]:-}"
  local -a out=()
  local line raw title link ep desc
  while IFS= read -r line; do
    [[ "$line" == ITEM:* ]] || continue
    raw="${line#ITEM:}"
    IFS=$'\x1e' read -r title link ep desc <<<"$raw"
    ai_item_keep "$title" "$desc" "$accept" "$kws" || continue
    out+=("$raw")
  done <<<"$(echo "$block" | grep '^ITEM:' || true)"
  echo "name=${AI_NAME[$sid]}"
  echo "icon=${AI_ICON[$sid]}"
  echo "count=${#out[@]}"
  local p
  for p in "${out[@]}"; do echo "ITEM:$p"; done
}

parse_ai_args() {
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
  local filter_raw="en,cn"
  [[ ${#args[@]} -gt 0 ]] && [[ "${args[0]}" =~ ^[0-9]+$ ]] && days="${args[0]}"
  if [[ ${#args[@]} -gt 0 ]] && ! [[ "${args[0]}" =~ ^[0-9]+$ ]]; then
    filter_raw="${args[0]}"
  fi
  if [[ ${#args[@]} -gt 1 ]]; then
    if [[ "${args[1]}" =~ ^[0-9]+$ ]]; then
      days="${args[1]}"
    else
      filter_raw="${args[1]}"
    fi
  fi
  local resolved
  resolved="$(resolve_max_sources "$cap")"
  echo "$days"
  echo "$filter_raw"
  echo "${resolved:-}"
}

main() {
  local -a pa=()
  mapfile -t pa < <(parse_ai_args "$@")
  local days="${pa[0]}"
  local filter_raw="${pa[1]}"
  local cap="${pa[2]:-}"

  local -A filt=()
  if [[ "$filter_raw" == "all" ]]; then
    local k
    for k in "${!AI_NAME[@]}"; do filt["$k"]=1; done
  else
    local x
    IFS=',' read -ra _parts <<<"${filter_raw// /}"
    for x in "${_parts[@]}"; do
      x="$(echo "$x" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
      [[ -n "$x" ]] && filt["$x"]=1
    done
  fi

  local -a order=()
  local sid
  for sid in "${AI_NEWS_SOURCE_ORDER[@]}"; do
    [[ -n "${filt[$sid]:-}" ]] || continue
    order+=("$sid")
  done
  mapfile -t order < <(apply_source_cap "$cap" "${order[@]}")

  export NEWS_FORMAT_MAX_ITEMS=10
  local -a blocks=()
  local fetch_out fb
  for sid in "${order[@]}"; do
    fetch_out="$(fetch_rss "${AI_NAME[$sid]}" "${AI_ICON[$sid]}" "${AI_URL[$sid]}" "$days" || true)"
    fb="$(ai_filter_block "$fetch_out" "$sid")"
    blocks+=("$fb")
  done

  local total=0
  local b c
  for b in "${blocks[@]}"; do
    c="$(echo "$b" | sed -n 's/^count=//p' | head -1)"
    total=$((total + ${c:-0}))
  done

  local out=""
  if [[ "$total" -eq 0 ]]; then
    out="今日无AI相关新资讯。"
  else
    out="📈 **AI / 技术资讯** · 共 ${total} 条"$'\n\n'
    out+="$(format_section_from_blocks "" "${blocks[@]}")"
  fi

  if [[ -n "$cap" ]]; then
    out="（本 run 抓取 ${#order[@]} 个源，上限 ${cap}）"$'\n\n'"$out"
  fi

  local appendix_on="${OPENCLAW_TECH_RSS_URL_APPENDIX:-1}"
  appendix_on="$(echo "$appendix_on" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  if [[ "$appendix_on" != "0" && "$appendix_on" != "false" && "$appendix_on" != "no" && "$appendix_on" != "off" && "$out" != *"今日无AI相关新资讯"* ]]; then
    local max_u=300
    local raw_max="${OPENCLAW_TECH_RSS_URL_APPENDIX_MAX:-}"
    raw_max="$(echo -n "$raw_max" | tr -d '[:space:]')"
    if [[ "$raw_max" =~ ^[0-9]+$ ]]; then
      max_u="$raw_max"
      [[ "$max_u" -lt 1 ]] && max_u=1
      [[ "$max_u" -gt 2000 ]] && max_u=2000
    fi
    mapfile -t url_lines < <(collect_urls_from_blocks "$max_u" "${blocks[@]}")
    out+="$(format_url_appendix_block "${url_lines[@]}")"
  fi

  printf '%s\n' "$out"
}

main "$@"
