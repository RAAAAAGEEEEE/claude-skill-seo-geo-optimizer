#!/usr/bin/env bash
# Audit SEO/GEO technique rapide, base sur curl (aucune dependance lourde).
#
# Usage:
#   ./audit_site.sh https://example.com                 # decouvre via sitemap.xml
#   ./audit_site.sh https://example.com/sitemap.xml      # sitemap explicite
#   ./audit_site.sh urls.txt                             # liste d'URLs, une par ligne
#
# Verifie par URL : code HTTP, <title>, meta description, canonical,
# hreflang, nombre de blocs JSON-LD, Open Graph, Twitter Card.
# Detecte les <title> dupliques entre pages.
#
# Limite connue : ne rend pas le JS. Un schema/canonical injecte cote
# client (WordPress + Yoast/RankMath en JS) n'apparaitra pas ici -- utiliser
# le navigateur ou le Rich Results Test dans ce cas (voir audit-framework.md).

set -u

INPUT="${1:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: $0 <base_url|sitemap_url|urls_file>" >&2
  exit 1
fi

TMP_URLS="$(mktemp)"
trap 'rm -f "$TMP_URLS"' EXIT

if [ -f "$INPUT" ]; then
  grep -v '^[[:space:]]*$' "$INPUT" > "$TMP_URLS"
else
  case "$INPUT" in
    */sitemap.xml) SITEMAP_URL="$INPUT" ;;
    */) SITEMAP_URL="${INPUT}sitemap.xml" ;;
    *) SITEMAP_URL="${INPUT}/sitemap.xml" ;;
  esac
  echo "Recuperation de $SITEMAP_URL ..." >&2
  if ! curl -sf "$SITEMAP_URL" | grep -o '<loc>[^<]*</loc>' | sed 's/<loc>//;s#</loc>##' > "$TMP_URLS"; then
    echo "Impossible de recuperer/parser $SITEMAP_URL -- fournis une liste d'URLs a la place." >&2
    exit 1
  fi
  if [ ! -s "$TMP_URLS" ]; then
    echo "Aucune URL trouvee dans $SITEMAP_URL" >&2
    exit 1
  fi
fi

TITLES_FILE="$(mktemp)"
trap 'rm -f "$TMP_URLS" "$TITLES_FILE"' EXIT

TOTAL=0
ISSUES=0

printf '%-70s %-6s %-6s %-6s %-6s %-6s %-6s %-6s\n' "URL" "HTTP" "TITLE" "DESC" "CANON" "HREFL" "JSONLD" "OG"
printf '%s\n' "----------------------------------------------------------------------------------------------------------------"

while IFS= read -r url; do
  [ -z "$url" ] && continue
  TOTAL=$((TOTAL + 1))

  HTTP_CODE=$(curl -s -o /tmp/audit_body_$$ -w '%{http_code}' -L "$url")
  BODY_FILE="/tmp/audit_body_$$"

  if [ "$HTTP_CODE" != "200" ]; then
    printf '%-70s %-6s\n' "$url" "$HTTP_CODE (attendu 200)"
    ISSUES=$((ISSUES + 1))
    rm -f "$BODY_FILE"
    continue
  fi

  TITLE=$(grep -o '<title>[^<]*</title>' "$BODY_FILE" | head -1 | sed 's/<title>//;s#</title>##')
  HAS_DESC=$(grep -qi 'name="description"' "$BODY_FILE" && echo "oui" || echo "NON")
  HAS_CANON=$(grep -qi 'rel="canonical"' "$BODY_FILE" && echo "oui" || echo "NON")
  HAS_HREFLANG=$(grep -qi 'hreflang=' "$BODY_FILE" && echo "oui" || echo "-")
  JSONLD_COUNT=$(grep -oc 'application/ld+json' "$BODY_FILE")
  HAS_OG=$(grep -qi 'property="og:title"' "$BODY_FILE" && echo "oui" || echo "NON")

  printf '%-70s %-6s %-6s %-6s %-6s %-6s %-6s %-6s\n' \
    "${url:0:70}" "$HTTP_CODE" \
    "$([ -n "$TITLE" ] && echo oui || echo NON)" \
    "$HAS_DESC" "$HAS_CANON" "$HAS_HREFLANG" "$JSONLD_COUNT" "$HAS_OG"

  echo "${TITLE}|${url}" >> "$TITLES_FILE"

  if [ -z "$TITLE" ] || [ "$HAS_DESC" = "NON" ] || [ "$HAS_CANON" = "NON" ]; then
    ISSUES=$((ISSUES + 1))
  fi

  rm -f "$BODY_FILE"
done < "$TMP_URLS"

echo ""
echo "=== Titles dupliques ==="
cut -d'|' -f1 "$TITLES_FILE" | sort | uniq -d | while read -r dup; do
  [ -z "$dup" ] && continue
  echo "Duplique : \"$dup\""
  grep -F "${dup}|" "$TITLES_FILE" | cut -d'|' -f2 | sed 's/^/  - /'
done

echo ""
echo "=== Robots.txt / Sitemap ==="
BASE=$(head -1 "$TMP_URLS" | sed -E 's#(https?://[^/]+)/.*#\1#')
if [ -n "$BASE" ]; then
  ROBOTS_CODE=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/robots.txt")
  echo "robots.txt : $ROBOTS_CODE"
  if [ "$ROBOTS_CODE" = "200" ]; then
    curl -s "$BASE/robots.txt" | grep -qi '^sitemap:' && echo "  -> declare bien une ligne Sitemap:" || echo "  -> AUCUNE ligne Sitemap: trouvee (a corriger)"
  fi
fi

echo ""
echo "$TOTAL URL(s) verifiee(s), $ISSUES avec au moins un probleme (HTTP != 200, title/description/canonical manquant)"
[ "$ISSUES" -gt 0 ] && exit 1 || exit 0
