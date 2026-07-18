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
  liste des bots IA (entraînement vs recherche/citation), sources.
- [scripts/validate_schema.py](scripts/validate_schema.py) — validateur
  JSON-LD local (champs requis par type schema.org).

## Périmètre

Ce skill audite et modifie le code du site courant (schema, meta, structure,
robots.txt/llms.txt, E-E-A-T). Il ne fait ni prospection ni digital PR ni
outreach — pour cette partie, voir un skill séparé dédié à l'acquisition.

## Licence

MIT
