#!/usr/bin/env bash
# Verifie les liens presents sur une page vers un domaine cible :
# dofollow vs nofollow, et repetition des ancres (signal de sur-optimisation).
#
# Usage:
#   ./check_backlinks.sh <url_ou_fichier_html> <domaine_cible>
#
# Exemple:
#   ./check_backlinks.sh https://annuaire-exemple.fr/fiche-123 siteservi.com
#
# Limite : parsing par grep/sed, pas un vrai parseur HTML -- suffisant pour
# une verification ponctuelle, pas pour un crawl a grande echelle (un outil
# comme Screaming Frog reste plus fiable pour de gros volumes).

set -u

SOURCE="${1:-}"
TARGET_DOMAIN="${2:-}"

if [ -z "$SOURCE" ] || [ -z "$TARGET_DOMAIN" ]; then
  echo "Usage: $0 <url_ou_fichier_html> <domaine_cible>" >&2
  exit 1
fi

TMP_HTML="$(mktemp)"
trap 'rm -f "$TMP_HTML"' EXIT

if [ -f "$SOURCE" ]; then
  cp "$SOURCE" "$TMP_HTML"
else
  if ! curl -sfL "$SOURCE" -o "$TMP_HTML"; then
    echo "Impossible de recuperer $SOURCE" >&2
    exit 1
  fi
fi

# Extrait les balises <a ...>texte</a> qui pointent vers le domaine cible
LINKS=$(grep -oiE '<a [^>]*href="[^"]*'"$TARGET_DOMAIN"'[^"]*"[^>]*>[^<]*</a>' "$TMP_HTML")

if [ -z "$LINKS" ]; then
  echo "Aucun lien vers $TARGET_DOMAIN trouve sur $SOURCE"
  exit 0
fi

TOTAL=0
DOFOLLOW=0
NOFOLLOW=0
ANCHORS_FILE="$(mktemp)"
trap 'rm -f "$TMP_HTML" "$ANCHORS_FILE"' EXIT

while IFS= read -r tag; do
  [ -z "$tag" ] && continue
  TOTAL=$((TOTAL + 1))
  if echo "$tag" | grep -qi 'rel="[^"]*nofollow'; then
    NOFOLLOW=$((NOFOLLOW + 1))
    STATUS="nofollow"
  else
    DOFOLLOW=$((DOFOLLOW + 1))
    STATUS="dofollow"
  fi
  ANCHOR=$(echo "$tag" | sed -E 's/.*>([^<]*)<\/a>/\1/' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  echo "$ANCHOR" >> "$ANCHORS_FILE"
  printf '[%s] "%s"\n' "$STATUS" "$ANCHOR"
done <<< "$LINKS"

echo ""
echo "=== Resume ==="
echo "Liens trouves vers $TARGET_DOMAIN : $TOTAL (dofollow: $DOFOLLOW, nofollow: $NOFOLLOW)"
if [ "$DOFOLLOW" -eq 0 ]; then
  echo "-> Aucun lien dofollow : valeur SEO quasi nulle depuis cette source."
fi

echo ""
echo "=== Repetition d'ancres (>1 occurrence = a surveiller) ==="
sort "$ANCHORS_FILE" | uniq -c | sort -rn | awk '$1 > 1 {$1=$1; print}'
