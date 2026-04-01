#!/usr/bin/env bash
# Bash 回退：安全资讯（RSS + NVD/CISA JSON，与 fetch_sec_news.py 对齐）。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../shared/bash_lib/news_rss_common.sh
source "$SCRIPT_DIR/../../shared/bash_lib/news_rss_common.sh"

need_cmd curl jq date gzip
command -v grep >/dev/null 2>&1 || die "需要 grep"

declare -A S_NAME S_URL S_ICON S_KIND

_reg() { local k="$1" n="$2" u="$3" i="$4" kind="${5:-rss}"
  S_NAME[$k]="$n"; S_URL[$k]="$u"; S_ICON[$k]="$i"; S_KIND[$k]="$kind"
}

_reg thn "The Hacker News" "https://thehackernews.com/feeds/posts/default?security" "🎯"
_reg bleeping "BleepingComputer" "https://www.bleepingcomputer.com/feed/" "💻"
_reg securityweek "SecurityWeek" "https://www.securityweek.com/feed/" "📰"
_reg krebson "Krebs on Security" "https://krebsonsecurity.com/feed/" "🔍"
_reg darkreading "Dark Reading" "https://www.darkreading.com/rss.xml" "🌑"
_reg threatpost "Threatpost" "https://threatpost.com/feed/" "⚠️"
_reg nakedsecurity "Naked Security" "https://nakedsecurity.sophos.com/feed/" "🕵️"
_reg helpnet "Help Net Security" "https://www.helpnetsecurity.com/feed/" "🔐"
_reg schneier "Schneier on Security" "https://www.schneier.com/feed/atom/" "🛡️"
_reg isc_sans "SANS ISC Diary" "https://isc.sans.edu/rssfeed_full.xml" "📡"
_reg securelist "Kaspersky Securelist" "https://securelist.com/feed/" "🕸️"
_reg welivesecurity "ESET WeLiveSecurity" "https://www.welivesecurity.com/feed/" "🦠"
_reg rapid7 "Rapid7 Blog" "https://blog.rapid7.com/rss/" "⚡"
_reg recordedfuture "Recorded Future" "https://www.recordedfuture.com/feed/" "🔮"
_reg anquanke "安全客" "https://www.anquanke.com/rss" "🔰"
_reg freebuf "FreeBuf" "https://www.freebuf.com/feed" "🧱"
_reg nsfocus "绿盟科技博客" "https://blog.nsfocus.net/feed/" "🟢"
_reg nvd "NVD CVE（recent JSON）" "" "🛡️" "json_nvd"
_reg cisa_kev "CISA KEV" "" "🇺🇸" "json_cisa_kev"
_reg tenable "Tenable Blog" "https://www.tenable.com/blog/feed" "🕵️"
_reg qualys "Qualys Blog" "https://blog.qualys.com/feed" "🏆"
_reg exploitdb "Exploit-DB" "https://www.exploit-db.com/rss.xml" "💉"
_reg unit42 "Palo Alto Unit 42" "https://unit42.paloaltonetworks.com/feed/" "🦅"
_reg socialengineer "Social-Engineer.org" "https://www.social-engineer.org/feed/" "🎭"
_reg trustsec "TrustedSec" "https://www.trustedsec.com/feed/" "✅"
_reg offsec "Offensive Security" "https://www.offensive-security.com/feed/" "⚔️"
_reg crowdstrike "CrowdStrike" "https://www.crowdstrike.com/blog/feed/" "🦅"
_reg sentinelone "SentinelOne" "https://www.sentinelone.com/feed/" "1️⃣"
_reg mandiant "Mandiant" "https://www.mandiant.com/feed" "🔥"
_reg csoonline "CSO Online" "https://www.csoonline.com/rss/security/" "🏢"

SEC_ORDER_all=(
  thn bleeping securityweek krebson darkreading threatpost nakedsecurity helpnet schneier isc_sans securelist welivesecurity
  rapid7 recordedfuture anquanke freebuf nsfocus nvd cisa_kev tenable qualys exploitdb unit42
  socialengineer trustsec offsec crowdstrike sentinelone mandiant csoonline
)
SEC_ORDER_vulns=(nvd cisa_kev anquanke freebuf nsfocus tenable qualys exploitdb unit42)
SEC_ORDER_attacks=(
  thn bleeping securityweek krebson darkreading threatpost nakedsecurity helpnet schneier isc_sans securelist welivesecurity
  rapid7 recordedfuture anquanke freebuf nsfocus
)
SEC_ORDER_se=(socialengineer trustsec offsec)
SEC_ORDER_tools=(crowdstrike sentinelone mandiant csoonline)

fetch_nvd_block() {
  local days="$1"
  local name="${S_NAME[nvd]}"
  local icon="${S_ICON[nvd]}"
  local url="${OPENCLAW_NVD_CVE_GZ_URL:-https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz}"
  local json
  if ! json="$(curl -fsSL --max-time 90 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' \
    -H 'Accept: application/json, application/gzip, */*' "$url" 2>/dev/null | gzip -dc 2>/dev/null)"; then
    echo "name=$name"
    echo "icon=$icon"
    echo "count=0"
    echo "error=nvd_fetch"
    return
  fi
  local -a pack=()
  local item pub id desc ep
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    pub="$(echo "$item" | jq -r '.publishedDate // empty')"
    id="$(echo "$item" | jq -r '.cve.CVE_data_meta.ID // "CVE"')"
    desc="$(echo "$item" | jq -r '([.cve.description.description_data[]? | select(.lang=="en") | .value] | first // "")' | head -c 400)"
    ep="$(parse_pub_date_epoch "$pub")"
    item_in_date_window "$ep" "$days" || continue
    pack+=("${id}"$'\x1e'"https://nvd.nist.gov/vuln/detail/${id}"$'\x1e'"${ep}"$'\x1e'"${desc}")
    [[ ${#pack[@]} -ge 120 ]] && break
  done < <(echo "$json" | jq -c '.CVE_Items[]?' 2>/dev/null | head -n 400)
  echo "name=$name"
  echo "icon=$icon"
  echo "count=${#pack[@]}"
  local p
  for p in "${pack[@]}"; do echo "ITEM:$p"; done
}

fetch_cisa_block() {
  local days="$1"
  local name="${S_NAME[cisa_kev]}"
  local icon="${S_ICON[cisa_kev]}"
  local url="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
  local json
  if ! json="$(curl -fsSL --max-time 60 -A 'Mozilla/5.0' "$url" 2>/dev/null)"; then
    echo "name=$name"
    echo "icon=$icon"
    echo "count=0"
    echo "error=cisa_fetch"
    return
  fi
  local -a pack=()
  local row title cve added ep vendor product desc
  while IFS= read -r row; do
    [[ -z "$row" ]] && continue
    cve="$(echo "$row" | jq -r '.cveID // empty')"
    title="$(echo "$row" | jq -r '.vulnerabilityName // .cveID')"
    added="$(echo "$row" | jq -r '.dateAdded // empty')"
    vendor="$(echo "$row" | jq -r '.vendorProject // ""')"
    product="$(echo "$row" | jq -r '.product // ""')"
    desc="$(echo "$row" | jq -r '.shortDescription // ""')"
    [[ -z "$desc" ]] && desc="${vendor} / ${product}"
    desc="${desc:0:400}"
    ep="$(parse_pub_date_epoch "${added}T00:00:00Z")"
    if [[ -z "$ep" && -n "$added" ]]; then
      ep="$(parse_pub_date_epoch "$added")"
    fi
    item_in_date_window "$ep" "$days" || continue
    local link="https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
    [[ "$cve" == CVE-* ]] && link="https://nvd.nist.gov/vuln/detail/${cve}"
    pack+=("${title}"$'\x1e'"${link}"$'\x1e'"${ep}"$'\x1e'"${desc}")
  done < <(echo "$json" | jq -c '.vulnerabilities[]?' 2>/dev/null)
  echo "name=$name"
  echo "icon=$icon"
  echo "count=${#pack[@]}"
  local p
  for p in "${pack[@]}"; do echo "ITEM:$p"; done
}

parse_sec_args() {
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

sec_source_order() {
  local c="$1"
  case "$c" in
    vulns) printf '%s\n' "${SEC_ORDER_vulns[@]}" ;;
    attacks) printf '%s\n' "${SEC_ORDER_attacks[@]}" ;;
    se) printf '%s\n' "${SEC_ORDER_se[@]}" ;;
    tools) printf '%s\n' "${SEC_ORDER_tools[@]}" ;;
    *) printf '%s\n' "${SEC_ORDER_all[@]}" ;;
  esac
}

main() {
  local -a pa=()
  mapfile -t pa < <(parse_sec_args "$@")
  local days="${pa[0]}"
  local category="${pa[1]}"
  local cap="${pa[2]:-}"

  local -a order=()
  mapfile -t order < <(sec_source_order "$category")
  mapfile -t order < <(apply_source_cap "$cap" "${order[@]}")

  export NEWS_FORMAT_MAX_ITEMS=6
  export NEWS_FORMAT_DESC_MAX=180

  local -a blocks=()
  local sid fetch_out
  for sid in "${order[@]}"; do
    fetch_out=""
    case "${S_KIND[$sid]:-rss}" in
      json_nvd) fetch_out="$(fetch_nvd_block "$days" || true)" ;;
      json_cisa_kev) fetch_out="$(fetch_cisa_block "$days" || true)" ;;
      *)
        fetch_out="$(fetch_rss "${S_NAME[$sid]}" "${S_ICON[$sid]}" "${S_URL[$sid]}" "$days" || true)"
        ;;
    esac
    blocks+=("$fetch_out")
  done

  local total=0
  local b c
  for b in "${blocks[@]}"; do
    c="$(echo "$b" | sed -n 's/^count=//p' | head -1)"
    total=$((total + ${c:-0}))
  done

  local today
  today="$(date +%m-%d)"
  local out=""
  out="🔒 安全资讯 ${today} | 共 ${total} 条"$'\n'$'\n'

  local bi=0
  local prev_group=""
  for sid in "${order[@]}"; do
    b="${blocks[$bi]}"
    bi=$((bi + 1))
    [[ "$(echo "$b" | grep -c '^ITEM:')" -eq 0 ]] && continue
    local group=1
    case "$sid" in
      nvd|cisa_kev|tenable|qualys|exploitdb|unit42) group=2 ;;
      socialengineer|trustsec|offsec) group=3 ;;
      crowdstrike|sentinelone|mandiant|csoonline) group=4 ;;
      *) group=1 ;;
    esac
    if [[ -n "$prev_group" && "$group" != "$prev_group" ]]; then
      out+=$'\n'
    fi
    prev_group="$group"
    mapfile -t _pf < <(parse_fetch_output "$b")
    local name="${_pf[0]:-}" icon="${_pf[1]:-}"
    local -a items=()
    local line raw
    while IFS= read -r line; do
      [[ "$line" == ITEM:* ]] || continue
      items+=("${line#ITEM:}")
    done <<<"$(echo "$b" | grep '^ITEM:')"
    [[ ${#items[@]} -eq 0 ]] && continue
    out+="$(format_source_block "$icon" "${name}（${#items[@]} 条）" "${items[@]}")"$'\n'$'\n'
  done

  out="$(echo -n "$out" | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}')"

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
    mapfile -t url_lines < <(collect_urls_from_blocks "$max_u" "${blocks[@]}")
    out+="$(format_url_appendix_block "${url_lines[@]}")"
  fi

  printf '%s\n' "$out"
}

main "$@"
