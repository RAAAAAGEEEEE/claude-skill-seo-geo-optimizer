# seo-geo-optimizer

Skill Claude Code : audit et implémentation SEO classique (Google) + GEO
(référencement génératif — citations par ChatGPT, Claude, Perplexity, Google
AI Overviews), directement dans un repo de site/app.

**État des connaissances : juillet 2026.** Les affirmations datées sont
vérifiées à leur source primaire ; les statistiques non sourçables ont été
retirées volontairement plutôt que conservées.

## Ce qui distingue ce skill

**Il vérifie l'accès réel des crawlers IA, pas seulement `robots.txt`.** Un
site peut autoriser explicitement `ClaudeBot` et lui renvoyer `403` via une
règle CDN — cas réel rencontré et documenté. Aucun audit HTML ne détecte ça ;
`check_ai_access.py` si.

Il privilégie la **donnée mesurée** (Search Console, CrUX, requêtes HTTP
réelles) sur l'inférence, et sépare explicitement les deux dans ses rapports.

## Installation

Copier ce dossier dans `~/.claude/skills/seo-geo-optimizer/` (tous projets)
ou dans `.claude/skills/` d'un projet spécifique.

## Démarrage rapide

```bash
# 1. Le site est-il seulement accessible aux moteurs génératifs ?
python scripts/check_ai_access.py https://example.com

# 2. Rapport consolidé (technique + schema + accès crawlers)
python scripts/generate_report.py --urls urls.txt --out-prefix audit --check-ai-access

# 3. Avec les données mesurées (accès requis)
python scripts/generate_report.py --urls urls.txt --out-prefix audit \
  --check-ai-access --crux-key "$CRUX_KEY" \
  --gsc-service-account creds.json --gsc-site "sc-domain:example.com"
```

## Scripts

| Script | Rôle | Accès requis |
|---|---|---|
| `check_ai_access.py` | Accès réel des crawlers IA, détecte le blocage CDN silencieux | aucun |
| `audit_site.sh` | Audit technique multi-URLs (curl) | aucun |
| `validate_schema.py` | Validation JSON-LD locale | aucun |
| `check_backlinks.sh` | dofollow/nofollow, répétition d'ancres | aucun |
| `generate_sitemap.py` | `sitemap.xml` + `robots.txt`, mono ou multi-sites | aucun |
| `crux_report.py` | Core Web Vitals terrain (utilisateurs réels) | clé API Google gratuite |
| `gsc_report.py` | Impressions, clics, positions réelles | compte de service GSC |
| `indexnow_submit.py` | Soumission Bing/Yandex/Naver/Seznam/Yep | clé IndexNow auto-hébergée |
| `generate_report.py` | **Rapport consolidé** Markdown + JSON | optionnel |

## Références

| Fichier | Contenu |
|---|---|
| `references/cloudflare-ai-access.md` | Blocage CDN des bots IA : diagnostic, correction, arbitrage |
| `references/ai-crawlers.md` | Bots entraînement vs recherche, robots.txt, statut réel de llms.txt |
| `references/audit-framework.md` | Audit technique / on-page / E-E-A-T |
| `references/schema-templates.md` | Blocs JSON-LD + statut par type (juillet 2026) |
| `references/indexing-rules.md` | Autorisé / interdit, IndexNow |
| `references/backlinks.md` | Évaluation de liens, PBN, annuaires |
| `references/data-hygiene.md` | Mesuré vs généré, péremption des recommandations |
| `references/gsc-access.md` | Mise en place du compte de service Search Console |
| `references/checklist.md` | Uniquement ce que les scripts ne peuvent pas vérifier |

## Périmètre

Audit et modification du site courant. **Pas** de prospection, digital PR ni
outreach — cela relève d'un skill séparé dédié à l'acquisition.

## Licence

MIT
