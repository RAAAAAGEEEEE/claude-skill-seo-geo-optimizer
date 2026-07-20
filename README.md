# seo-geo-optimizer

Claude Code skill: audite et implémente les optimisations SEO classique
(Google) et GEO (référencement génératif — citations par ChatGPT, Claude,
Perplexity, Google AI Overviews) directement dans un repo de site/app.

## Installation

Copier ce dossier dans `~/.claude/skills/seo-geo-optimizer/` (disponible sur
tous les projets Claude Code) ou dans `.claude/skills/` à la racine d'un
projet spécifique.

## Contenu

- [SKILL.md](SKILL.md) — point d'entrée, workflow, leviers par ordre de ROI.
- [references/checklist.md](references/checklist.md) — pass d'audit rapide.
- [references/audit-framework.md](references/audit-framework.md) — audit
  technique/on-page/E-E-A-T détaillé.
- [references/schema-templates.md](references/schema-templates.md) — blocs
  JSON-LD paste-ready (LocalBusiness, Organization, FAQPage, Product,
  Article, HowTo, BreadcrumbList).
- [references/ai-crawlers.md](references/ai-crawlers.md) — robots.txt/llms.txt,
  liste des bots IA (entraînement vs recherche/citation), soumission Brave
  Search (GEO), sources.
- [references/indexing-rules.md](references/indexing-rules.md) — méthode
  d'indexation correcte, interdictions (Google Indexing API, auto-submit).
- [references/backlinks.md](references/backlinks.md) — cadre backlinks
  (interne/externe, dofollow, PBN, annuaires, à bannir).
- [references/data-hygiene.md](references/data-hygiene.md) — mesuré vs
  généré IA, audit périodique de la base de connaissances.
- [scripts/validate_schema.py](scripts/validate_schema.py) — validateur
  JSON-LD local (champs requis par type schema.org).
- [scripts/audit_site.sh](scripts/audit_site.sh) — audit technique
  multi-URLs en bash/curl (HTTP, title, description, canonical, hreflang,
  JSON-LD, OG, robots.txt/sitemap).
- [scripts/generate_sitemap.py](scripts/generate_sitemap.py) — génère
  `sitemap.xml` (+ `robots.txt` optionnel), un ou multi-sites.
- [scripts/check_backlinks.sh](scripts/check_backlinks.sh) — vérifie
  dofollow/nofollow et répétition d'ancres sur une page source.

## Périmètre

Ce skill audite et modifie le code du site courant (schema, meta, structure,
robots.txt/llms.txt, E-E-A-T). Il ne fait ni prospection ni digital PR ni
outreach — pour cette partie, voir un skill séparé dédié à l'acquisition.

## Licence

MIT
