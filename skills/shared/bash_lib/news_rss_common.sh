# Shared RSS/bash helpers for global-news and tech-rss-news (sourced, not executed alone).
# Callers: set -euo pipefail; need_cmd curl jq date; command -v grep ...

DEFAULT_NEWS_LOOKBACK_DAYS=3
RULE="────────────────────────────────────────"

die() { echo "$*" >&2; exit 1; }

need_cmd() {
  local c
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || die "需要安装命令: $c（bash 脚本依赖系统工具，非 Python/Node）"
  done
}


# --- html / text ---
html_unescape_simple() {
  sed -e 's/&lt;/</g' -e 's/&gt;/>/g' -e 's/&amp;/\&/g' -e 's/&quot;/"/g' -e "s/&#39;/'/g" <<<"${1:-}"
}

strip_tags() {
  sed -e 's/<[^>]*>//g' <<<"${1:-}"
}

clean_whitespace() {
  local t
  t="$(echo -n "${1:-}" | tr -s '[:space:]' ' ' | sed 's/^ *//;s/ *$//')"
  printf '%s' "$t"
}

clean_url() {
  local u="${1:-}"
  u="$(echo -n "$u" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [[ -z "$u" ]] && { echo ""; return; }
  if [[ "$u" == *"?"* ]]; then
    echo "${u%%\?*}"
  else
    echo "$u"
  fi
}

first_http_from_description() {
  local h="$1"
  [[ -z "$h" ]] && { echo ""; return; }
  if [[ "$h" =~ href=[\"\']?(https?://[^\"\'\>[:space:]]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    echo ""
  fi
}

# --- dates (GNU date) ---
parse_pub_date_epoch() {
  local s
  s="$(clean_whitespace "${1:-}")"
  [[ -z "$s" ]] && { echo ""; return; }
  local out=""
  out="$(date -d "$s" +%s 2>/dev/null)" || out=""
  [[ -n "$out" ]] && { echo "$out"; return; }
  # ISO Z
  if [[ "$s" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T ]]; then
    out="$(date -d "${s/Z/ UTC}" +%s 2>/dev/null)" || out=""
    [[ -n "$out" ]] && { echo "$out"; return; }
  fi
  echo ""
}

item_in_date_window() {
  local pub_epoch="$1"
  local days_ago="$2"
  if [[ "$days_ago" -lt 0 ]]; then
    return 0
  fi
  [[ -z "$pub_epoch" ]] && return 1
  local now sec
  now="$(date +%s)"
  if [[ "$days_ago" -eq 0 ]]; then
    local start
    start="$(date -d "today 0" +%s)"
    [[ "$pub_epoch" -ge "$start" ]]
    return
  fi
  sec=$((days_ago * 86400))
  [[ "$pub_epoch" -ge $((now - sec)) ]]
}

format_datetime() {
  local ep="$1"
  [[ -z "$ep" ]] && { echo "未知"; return; }
  date -d "@$ep" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "未知"
}

# --- argv ---
parse_argv_max_sources() {
  local -a rest=()
  local cap=""
  local -a argv=("$@")
  local i=0
  while [[ $i -lt ${#argv[@]} ]]; do
    local a="${argv[$i]}"
    if [[ "$a" =~ ^--max-sources=([0-9]+)$ ]]; then
      cap="${BASH_REMATCH[1]}"
      ((i++)) || true
      continue
    fi
    if [[ "$a" == "--max-sources" && $((i + 1)) -lt ${#argv[@]} ]] && [[ "${argv[$((i + 1))]}" =~ ^[0-9]+$ ]]; then
      cap="${argv[$((i + 1))]}"
      ((i += 2)) || true
      continue
    fi
    rest+=("$a")
    ((i++)) || true
  done
  if [[ -n "$cap" && "$cap" -le 0 ]]; then cap=""; fi
  printf '%s\n' "${rest[@]}"
  echo "--CAP--"
  echo "${cap:-}"
}

resolve_max_sources() {
  local cli_cap="$1"
  if [[ -n "$cli_cap" ]]; then
    echo "$cli_cap"
    return
  fi
  local raw="${OPENCLAW_NEWS_MAX_SOURCES:-}"
  raw="$(echo -n "$raw" | tr -d '[:space:]')"
  if [[ -z "$raw" || ! "$raw" =~ ^[0-9]+$ || "$raw" == "0" ]]; then
    echo ""
  else
    echo "$raw"
  fi
}

apply_source_cap() {
  local cap="$1"
  shift
  local -a order=("$@")
  if [[ -z "$cap" ]]; then
    printf '%s\n' "${order[@]}"
    return
  fi
  local -a out=()
  local n=0
  local x
  for x in "${order[@]}"; do
    [[ $n -ge $cap ]] && break
    out+=("$x")
    ((n++)) || true
  done
  printf '%s\n' "${out[@]}"
}
# --- RSS: xpath helpers ---
rss_item_count() {
  local xml="$1"
  local n
  n="$(xmllint --xpath "count(//*[local-name()='item'])" "$xml" 2>/dev/null | tail -1 | tr -d '[:space:]')"
  if [[ "$n" =~ ^[0-9]+$ && "$n" -gt 0 ]]; then
    echo "$n"
    return
  fi
  n="$(xmllint --xpath "count(//*[local-name()='entry'])" "$xml" 2>/dev/null | tail -1 | tr -d '[:space:]')"
  if [[ "$n" =~ ^[0-9]+$ ]]; then
    echo "$n"
  else
    echo 0
  fi
}

rss_item_tag() {
  local xml="$1"
  local n
  n="$(xmllint --xpath "count(//*[local-name()='item'])" "$xml" 2>/dev/null | tail -1 | tr -d '[:space:]')"
  if [[ "$n" =~ ^[0-9]+$ && "$n" -gt 0 ]]; then
    echo item
    return
  fi
  echo entry
}

get_item_title() {
  local xml="$1" i="$2" itag="$3"
  local t
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='title'])" "$xml" 2>/dev/null)"
  echo "$(clean_whitespace "$(html_unescape_simple "$t")")"
}

get_item_pub_raw() {
  local xml="$1" i="$2" itag="$3"
  local t=""
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='pubDate'])" "$xml" 2>/dev/null)"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$(clean_whitespace "$t")"; return; }
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='published'])" "$xml" 2>/dev/null)"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$(clean_whitespace "$t")"; return; }
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='updated'])" "$xml" 2>/dev/null)"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$(clean_whitespace "$t")"; return; }
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='date'])" "$xml" 2>/dev/null)"
  echo "$(clean_whitespace "$t")"
}

get_item_description_raw() {
  local xml="$1" i="$2" itag="$3"
  local t
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='description'])" "$xml" 2>/dev/null)"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$t"; return; }
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='summary'])" "$xml" 2>/dev/null)"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$t"; return; }
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='encoded'])" "$xml" 2>/dev/null)"
  echo "$t"
}

get_item_link() {
  local xml="$1" i="$2" itag="$3"
  local d_raw="$4"
  local t href
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='link'])" "$xml" 2>/dev/null)"
  t="$(clean_whitespace "$t")"
  if [[ "$t" =~ ^https?:// ]]; then
    clean_url "$t"
    return
  fi
  href="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='link'][@rel='alternate']/@href)" "$xml" 2>/dev/null)"
  href="$(clean_whitespace "$href")"
  if [[ -n "$href" ]]; then
    clean_url "$href"
    return
  fi
  href="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='link'][1]/@href)" "$xml" 2>/dev/null)"
  href="$(clean_whitespace "$href")"
  if [[ -n "$href" ]]; then
    clean_url "$href"
    return
  fi
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='guid'])" "$xml" 2>/dev/null)"
  t="$(clean_whitespace "$t")"
  if [[ "$t" =~ ^https?:// ]]; then
    clean_url "$t"
    return
  fi
  t="$(xmllint --xpath "string(//*[local-name()='$itag'][$i]/*[local-name()='id'])" "$xml" 2>/dev/null)"
  t="$(clean_whitespace "$t")"
  if [[ "$t" =~ ^https?:// ]]; then
    clean_url "$t"
    return
  fi
  first_http_from_description "$d_raw"
}

rss_grep_one_line() {
  tr '\n' ' ' <<<"${1:-}" | tr -s ' '
}

rss_grep_block_title() {
  local b="$1"
  local line t
  line="$(rss_grep_one_line "$b")"
  t="$(sed -n 's:.*<title[^>]*><!\[CDATA\[\([^]]*\)\]\].*:\1:p' <<<"$line")"
  t="$(clean_whitespace "$t")"
  if [[ -n "$t" ]]; then html_unescape_simple "$t"; return; fi
  t="$(sed -n 's:.*<title[^>]*>\([^<]*\)</title>.*:\1:p' <<<"$line")"
  html_unescape_simple "$(clean_whitespace "$t")"
}

rss_grep_block_description() {
  local b="$1"
  local line t
  line="$(rss_grep_one_line "$b")"
  t="$(sed -n 's:.*<description[^>]*><!\[CDATA\[\(.\{0,12000\}\)\]\].*:\1:p' <<<"$line")"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$t"; return; }
  t="$(sed -n 's:.*<description[^>]*>\([^<]*\)</description>.*:\1:p' <<<"$line")"
  echo "$t"
}

rss_grep_block_pub_raw() {
  local b="$1"
  local line t
  line="$(rss_grep_one_line "$b")"
  t="$(sed -n 's:.*<pubDate[^>]*>\([^<]*\)</pubDate>.*:\1:p' <<<"$line")"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$(clean_whitespace "$t")"; return; }
  t="$(sed -n 's:.*<published[^>]*>\([^<]*\)</published>.*:\1:p' <<<"$line")"
  [[ -n "$(clean_whitespace "$t")" ]] && { echo "$(clean_whitespace "$t")"; return; }
  t="$(sed -n 's:.*<updated[^>]*>\([^<]*\)</updated>.*:\1:p' <<<"$line")"
  echo "$(clean_whitespace "$t")"
}

rss_grep_block_link() {
  local b="$1"
  local d_raw="$2"
  local line t href
  line="$(rss_grep_one_line "$b")"
  t="$(sed -n 's:.*<link[^>]*>\([^<]*\)</link>.*:\1:p' <<<"$line")"
  t="$(clean_whitespace "$t")"
  if [[ "$t" =~ ^https?:// ]]; then echo "$t"; return; fi
  href="$(sed -n 's:.*<link[^>]*href="\([^"]*\)".*:\1:p' <<<"$line" | head -1)"
  href="$(clean_whitespace "$href")"
  if [[ -n "$href" ]]; then echo "$href"; return; fi
  t="$(sed -n 's:.*<guid[^>]*>\([^<]*\)</guid>.*:\1:p' <<<"$line")"
  t="$(clean_whitespace "$t")"
  if [[ "$t" =~ ^https?:// ]]; then echo "$t"; return; fi
  t="$(sed -n 's:.*<id[^>]*>\([^<]*\)</id>.*:\1:p' <<<"$line")"
  t="$(clean_whitespace "$t")"
  if [[ "$t" =~ ^https?:// ]]; then echo "$t"; return; fi
  first_http_from_description "$d_raw"
}

rss_grep_process_block() {
  local block="$1"
  local days="$2"
  local -n _pack="$3"
  local title desc_raw pub_raw link desc ep
  title="$(rss_grep_block_title "$block")"
  [[ -z "$title" ]] && return
  desc_raw="$(rss_grep_block_description "$block")"
  pub_raw="$(rss_grep_block_pub_raw "$block")"
  ep="$(parse_pub_date_epoch "$pub_raw")"
  if ! item_in_date_window "$ep" "$days"; then
    return
  fi
  link="$(rss_grep_block_link "$block" "$desc_raw")"
  desc="$(strip_tags "$desc_raw")"
  desc="${desc:0:1200}"
  _pack+=("${title}"$'\x1e'"${link}"$'\x1e'"${ep}"$'\x1e'"${desc}")
}

fetch_rss_grep_fill() {
  local tmp="$1" days="$2"
  local -n _pack="$3"
  local n_item n_entry use_entry block
  # 大文件上 grep -Pzo 可能极慢，截断后再解析
  local sz
  sz="$(wc -c <"$tmp" | tr -d ' ')"
  if [[ "${sz:-0}" -gt 4000000 ]]; then
    local t2
    t2="$(mktemp)"
    head -c 4000000 "$tmp" >"$t2"
    mv "$t2" "$tmp"
  fi
  n_item=$(grep -o '<item[^>]*>' "$tmp" 2>/dev/null | wc -l | tr -d ' ')
  n_entry=$(grep -o '<entry[^>]*>' "$tmp" 2>/dev/null | wc -l | tr -d ' ')
  use_entry=0
  if [[ "${n_entry:-0}" -gt "${n_item:-0}" ]]; then use_entry=1; fi

  if [[ $use_entry -eq 0 ]]; then
    while IFS= read -r -d '' block; do
      [[ -z "$block" ]] && continue
      rss_grep_process_block "$block" "$days" "$3"
    done < <(LC_ALL=C grep -Pzo '(?s)<item[^>]*>.*?</item>' "$tmp" 2>/dev/null || true)
  else
    while IFS= read -r -d '' block; do
      [[ -z "$block" ]] && continue
      rss_grep_process_block "$block" "$days" "$3"
    done < <(LC_ALL=C grep -Pzo '(?s)<entry[^>]*>.*?</entry>' "$tmp" 2>/dev/null || true)
  fi
}

fetch_rss_xmllint_fill() {
  local tmp="$1" days="$2"
  local -n _pack="$3"
  local itag n i title desc_raw pub_raw link desc ep
  itag="$(rss_item_tag "$tmp")"
  n="$(rss_item_count "$tmp")"
  if [[ ! "$n" =~ ^[0-9]+$ ]]; then n=0; fi
  for ((i = 1; i <= n; i++)); do
    title="$(get_item_title "$tmp" "$i" "$itag")"
    [[ -z "$title" ]] && continue
    desc_raw="$(get_item_description_raw "$tmp" "$i" "$itag")"
    pub_raw="$(get_item_pub_raw "$tmp" "$i" "$itag")"
    ep="$(parse_pub_date_epoch "$pub_raw")"
    if ! item_in_date_window "$ep" "$days"; then
      continue
    fi
    link="$(get_item_link "$tmp" "$i" "$itag" "$desc_raw")"
    desc="$(strip_tags "$desc_raw")"
    desc="${desc:0:1200}"
    _pack+=("${title}"$'\x1e'"${link}"$'\x1e'"${ep}"$'\x1e'"${desc}")
  done
}

core_summary_lines() {
  local title="$1"
  local description="$2"
  local desc_max="${3:-480}"
  local t d excerpt
  t="$(clean_whitespace "$(html_unescape_simple "$title")")"
  [[ -z "$t" ]] && t="（无标题）"
  d="$(clean_whitespace "$(html_unescape_simple "$(strip_tags "$description")")")"
  if [[ -n "$d" && ${#d} -ge 20 ]]; then
    local pfx="${t:0:20}"
    if [[ "${d,,}" == "${pfx,,}"* && ${#d} -le $((${#t} + 5)) ]]; then
      d=""
    elif [[ "${d,,}" == *"${t,,}"* && ${#d} -lt $((${#t} + 30)) ]]; then
      d=""
    fi
  fi
  echo "摘要 · $t"
  if [[ -n "$d" ]]; then
    if [[ ${#d} -le $desc_max ]]; then
      excerpt="$d"
    else
      excerpt="${d:0:$((desc_max - 1))}…"
    fi
    echo "      $excerpt"
  fi
}

format_news_item_lines() {
  local idx="$1" title="$2" description="$3" pub_epoch="$4" url="$5"
  local desc_max="${6:-480}"
  local link
  link="$(clean_url "$url")"
  echo "【$idx】"
  if [[ -n "$link" ]]; then
    echo "$link"
  fi
  mapfile -t _cs < <(core_summary_lines "$title" "$description" "$desc_max")
  local _ln
  for _ln in "${_cs[@]}"; do echo "$_ln"; done
  echo "时间 · $(format_datetime "$pub_epoch")"
  if [[ -n "$link" ]]; then
    echo "[阅读原文]($link)"
  fi
  echo "链接 · ${link:-（无）}"
  if [[ -n "$link" ]]; then
    echo "$link"
  fi
}

format_source_block() {
  local icon="$1"
  local source_name="$2"
  shift 2
  local -a items_ref=("$@")
  echo "$icon **$source_name**"
  local n=0 idx=1
  local max_items="${NEWS_FORMAT_MAX_ITEMS:-8}"
  local desc_max="${NEWS_FORMAT_DESC_MAX:-480}"
  local it
  for it in "${items_ref[@]}"; do
    [[ $n -ge $max_items ]] && break
    IFS=$'\x1e' read -r title link ep desc <<<"$it"
    [[ -z "$title" ]] && continue
    if [[ $n -gt 0 ]]; then echo ""; fi
    echo "$RULE"
    mapfile -t _bl < <(format_news_item_lines "$idx" "$title" "$desc" "$ep" "$link" "$desc_max")
    local _ln
    for _ln in "${_bl[@]}"; do echo "$_ln"; done
    n=$((n + 1))
    idx=$((idx + 1))
  done
}

fetch_rss() {
  local name="$1" icon="$2" feed_url="$3" days="$4"
  local tmp err content
  tmp="$(mktemp)"
  err=""
  if ! content="$(curl -fsSL --max-time 20 -A "Mozilla/5.0" -H "Accept: application/rss+xml, application/xml, text/xml, */*" "$feed_url" 2>&1)"; then
    echo "name=$name"
    echo "icon=$icon"
    echo "count=0"
    echo "error=$content"
    rm -f "$tmp"
    return
  fi
  printf '%s' "$content" >"$tmp"
  if command -v xmllint >/dev/null 2>&1; then
    if ! xmllint --noout "$tmp" 2>/dev/null; then
      if [[ "$content" =~ \<rss ]]; then
        local frag
        frag="$(echo "$content" | sed -n '/<rss/,/<\/rss>/p' | head -c 12000000)"
        printf '%s' "$frag" >"$tmp"
      fi
    fi
  fi
  local -a pack=()
  if command -v xmllint >/dev/null 2>&1; then
    fetch_rss_xmllint_fill "$tmp" "$days" pack
  else
    fetch_rss_grep_fill "$tmp" "$days" pack
  fi
  rm -f "$tmp"
  echo "name=$name"
  echo "icon=$icon"
  echo "count=${#pack[@]}"
  local p
  for p in "${pack[@]}"; do echo "ITEM:$p"; done
}

fetch_sina() {
  local name="$1" icon="$2" lid="$3" days="$4"
  local api url json
  api="https://feed.mix.sina.com.cn/api/roll/get"
  url="${api}?pageid=153&lid=${lid}&num=20&page=1"
  if ! json="$(curl -fsSL --max-time 20 -A "Mozilla/5.0" -H "Referer: https://news.sina.com.cn" "$url" 2>&1)"; then
    echo "name=$name"
    echo "icon=$icon"
    echo "count=0"
    echo "error=$json"
    return
  fi
  local -a pack=()
  local title link ctime ep
  while IFS=$'\t' read -r title link ctime; do
    [[ -z "$title" ]] && continue
    ep=""
    if [[ -n "$ctime" && "$ctime" =~ ^[0-9]+$ ]]; then
      ep="$ctime"
    fi
    if ! item_in_date_window "$ep" "$days"; then
      continue
    fi
    pack+=("${title}"$'\x1e'"${link}"$'\x1e'"${ep}"$'\x1e'"")
  done < <(echo "$json" | jq -r '.result.data[]? | [.title // "", .url // "", .ctime // ""] | @tsv' 2>/dev/null)
  echo "name=$name"
  echo "icon=$icon"
  echo "count=${#pack[@]}"
  local p
  for p in "${pack[@]}"; do echo "ITEM:$p"; done
}

parse_fetch_output() {
  local block="$1"
  local name icon count err
  name="$(echo "$block" | sed -n 's/^name=//p' | head -1)"
  icon="$(echo "$block" | sed -n 's/^icon=//p' | head -1)"
  count="$(echo "$block" | sed -n 's/^count=//p' | head -1)"
  err="$(echo "$block" | sed -n 's/^error=//p' | head -1)"
  echo "$name"
  echo "$icon"
  echo "$count"
  echo "$err"
}

format_section_from_blocks() {
  local title="$1"
  shift
  local -a blocks=("$@")
  local b out name icon count body
  out="$title"$'\n'$'\n'
  local first=1
  for b in "${blocks[@]}"; do
    mapfile -t _pf < <(parse_fetch_output "$b")
    name="${_pf[0]:-}"
    icon="${_pf[1]:-}"
    # 与 Python format_section 一致：count==0 的源不展示（含抓取失败）
    if [[ "$(echo "$b" | grep -c '^ITEM:')" -eq 0 ]]; then
      continue
    fi
    local -a items=()
    local line raw
    while IFS= read -r line; do
      [[ "$line" == ITEM:* ]] || continue
      raw="${line#ITEM:}"
      items+=("$raw")
    done <<<"$(echo "$b" | grep '^ITEM:')"
    [[ ${#items[@]} -eq 0 ]] && continue
    [[ $first -eq 0 ]] && out+=$'\n'
    body="$(format_source_block "$icon" "${name}（${#items[@]} 条）" "${items[@]}")"
    out+="$body"$'\n'$'\n'
    first=0
  done
  echo -n "$out" | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}' | sed -e :a -e '/^\s*$/{$d;N;ba' -e '}'
}

collect_urls_from_blocks() {
  local max_u="$1"
  shift
  local -a blocks=("$@")
  local -a seen=()
  local b line raw link u n
  n=0
  for b in "${blocks[@]}"; do
    while IFS= read -r line; do
      [[ "$line" == ITEM:* ]] || continue
      raw="${line#ITEM:}"
      IFS=$'\x1e' read -r _title link _ep _desc <<<"$raw"
      link="$(clean_url "$link")"
      [[ "$link" =~ ^https?:// ]] || continue
      local dup=0
      for u in "${seen[@]}"; do [[ "$u" == "$link" ]] && dup=1 && break; done
      [[ $dup -eq 1 ]] && continue
      seen+=("$link")
      echo "$link"
      n=$((n + 1))
      [[ $n -ge $max_u ]] && return
    done <<<"$(echo "$b" | grep '^ITEM:')"
  done
}

format_url_appendix_block() {
  local -a urls=("$@")
  [[ ${#urls[@]} -eq 0 ]] && return
  echo ""
  echo ""
  echo "$RULE"
  echo "🔗 **原文链接汇总（纯文本，每行一个 URL，可复制）**"
  echo "（若上方被摘要，请至少保留本段。）"
  echo ""
  local u
  for u in "${urls[@]}"; do echo "$u"; done
}
