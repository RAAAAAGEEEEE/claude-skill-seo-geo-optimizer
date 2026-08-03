---
name: seo-geo-optimizer
description: >
  Audite et implémente les optimisations SEO classique (Google) et GEO
  (référencement génératif : citations par ChatGPT, Claude, Perplexity,
  Google AI Overviews) sur un site/codebase. À utiliser quand l'utilisateur
  veut auditer puis corriger un site : accès réel des crawlers IA (blocage
  CDN), schema JSON-LD, meta, structure de contenu, E-E-A-T, Core Web Vitals
  mesurés, Search Console. Couvre sites vitrines, SaaS, e-commerce et
  commerces locaux. Ne pas confondre avec le skill `SEO` (moteur autonome de
  prospection/digital PR/outreach via `/SEO`) : ce skill-ci audite et modifie
  le code du site courant, il ne fait ni prospection ni outreach.
---

# SEO / GEO Optimizer

**État des connaissances : juillet 2026.** Les recommandations SEO se
périment vite (voir §Péremption). Chaque affirmation datée ci-dessous a été
vérifiée à sa source primaire, pas reprise d'un blog.

## Principe directeur
Deux fronts simultanés : ranker sur Google **et** être cité par les moteurs
génératifs. En 2026 le second n'est plus optionnel — le taux de recherches
Google sans aucun clic atteint ~65%, et ~93% en AI Mode. Mais l'ordre compte :
**un site que les crawlers IA ne peuvent pas atteindre a un plafond de zéro**,
quelle que soit la qualité de son contenu. On vérifie l'accès avant tout le
reste.

## Ce skill vs les autres skills SEO
- **`seo-geo-optimizer`** (ici) : audit + implémentation on-site.
- **`SEO`** (`/SEO`) : prospection éditoriale, digital PR, outreach. Ne
  touche pas au code.
- Sur un même projet : ce skill d'abord (le site doit être solide et
  accessible), `/SEO` ensuite.

## Workflow
1. **Vérifier l'accès réel** — `scripts/check_ai_access.py`. C'est le
   prérequis, pas une étape parmi d'autres.
2. **Explorer** le repo : stack, templates, `robots.txt`, `sitemap.xml`,
   head/meta, schema existant.
3. **Auditer** → `scripts/generate_report.py` produit `AUDIT_GEO.md` +
   JSON. Ne pas rédiger l'audit à la main : il doit être re-exécutable.
4. **Attendre le GO** avant de coder. L'audit priorise, il ne modifie rien.
5. **Modifier par lots**, un diff à la fois.
6. Toute décision à impact produit (blocage de crawlers, migration d'URLs,
   suppression de pages) → exposer le pour/contre, **ne pas trancher seul**.

## Les leviers, par ordre de ROI réel

### 1. Accès effectif des crawlers IA — prérequis absolu
`robots.txt` déclare une intention ; le CDN décide de la réalité. Un site
peut autoriser explicitement `ClaudeBot` et lui renvoyer `403` via une règle
Cloudflare, sans que personne ne le voie. Cas réel documenté dans
[references/cloudflare-ai-access.md](references/cloudflare-ai-access.md).
- **Échéance à connaître** : depuis le 15 septembre 2026, Cloudflare bascule
  les nouveaux sites et les comptes gratuits vers un blocage par défaut des
  crawlers d'entraînement et d'agents IA. Un site peut changer de
  comportement sans action de son propriétaire.
- Distinguer bots d'**entraînement** (`GPTBot`, `ClaudeBot`,
  `Google-Extended`) et bots de **recherche/citation** (`OAI-SearchBot`,
  `Claude-SearchBot`, `PerplexityBot`, `*-User`). Bloquer les seconds =
  impossible d'être cité. Liste complète :
  [references/ai-crawlers.md](references/ai-crawlers.md).
- Diagnostic : `python scripts/check_ai_access.py https://example.com`

### 2. Fondamentaux techniques et on-page
Title unique, meta description, canonical, un seul H1, hiérarchie logique,
sitemap à jour référencé dans `robots.txt`, HTTPS, pas de duplication.
Rien de nouveau, mais c'est ce qui casse le plus souvent. Automatisé par
`scripts/audit_site.sh` et `scripts/generate_report.py`. Détail :
[references/audit-framework.md](references/audit-framework.md).

Site multilingue : vérifier la réciprocité hreflang
(`generate_report.py` le fait automatiquement) — **75% des sites
internationaux ont une erreur hreflang**, l'erreur technique la plus
fréquente du domaine.

### 3. Schema JSON-LD — priorités réévaluées (juillet 2026)
JSON-LD uniquement. Un schema **déployé** n'est pas un schema **valide** :
toujours valider (`scripts/validate_schema.py` ou Rich Results Test).

**Types qui produisent encore des rich results Google** — c'est là qu'est le
ROI mesurable : `Product` (+ `AggregateRating`), `Article`/`BlogPosting`,
`BreadcrumbList`, `Organization`, `LocalBusiness`, `Event`, `JobPosting`,
`Video`, `Recipe`.

**Types dépréciés côté rich results Google** — ne plus les vendre comme un
gain SERP :
- `FAQPage` : rich results supprimés le **7 mai 2026**, documentation
  Google retirée le 15 juin 2026. Le type schema.org reste valide et reste
  lu par Bing et les crawlers IA — le conserver est légitime, le présenter
  comme un levier de ranking Google ne l'est plus.
- `HowTo` : déprécié depuis septembre 2023, zéro gain SERP.

Templates : [references/schema-templates.md](references/schema-templates.md).

### 4. Structure de contenu pour le retrieval IA
Les moteurs génératifs lisent des passages isolément. Réponse directe en
tête de section, contexte ensuite ; FAQ en vrai Q→R ; contenu factuel, daté,
sourcé. Position officielle de Google (guide « AI features », juin 2026) :
*« You don't need to create new machine readable files, AI text files, or
markup to appear in these features »* — autrement dit, pas de format magique,
les fondamentaux SEO suffisent côté Google. Ne jamais promettre l'inverse.

### 5. E-E-A-T
Page À-propos réelle, mentions légales complètes (éditeur, hébergeur,
numéro d'immatriculation si applicable), auteur identifiable, NAP cohérent
en local, date de mise à jour visible. Détail :
[references/audit-framework.md](references/audit-framework.md#e-e-a-t).
Commerce local : Google Business Profile a une API, mais avec un délai
d'approbation manuel Google à anticiper —
[references/google-business-profile.md](references/google-business-profile.md).

### 6. Performance mesurée
Core Web Vitals **terrain** (utilisateurs réels) via l'API CrUX, pas une
simulation Lighthouse : `scripts/crux_report.py`. Seuils « bon » : LCP
≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1. Si CrUX ne retourne rien, c'est un trafic
insuffisant — le dire, ne pas le confondre avec un problème de perf.

### 7. Autorité et backlinks — évaluation, pas acquisition
Ce skill **évalue** un lien (dofollow ? ancre sur-optimisée ? risque PBN ?),
il ne le **cherche** pas : c'est le rôle de `/SEO`. Cadre :
[references/backlinks.md](references/backlinks.md), vérification :
`scripts/check_backlinks.sh`.

## Indexation — ce qui est autorisé, ce qui ne l'est pas
- **Google** : sitemap + Search Console uniquement. **Ne jamais** utiliser
  la Google Indexing API hors `JobPosting`/`BroadcastEvent` (usage détourné,
  risque de coupure d'accès), **ne jamais** coder d'auto-submit maison.
- **Bing, Yandex, Naver, Seznam, Yep** : IndexNow est le mécanisme prévu et
  légitime, gratuit et automatisable — `scripts/indexnow_submit.py`. Google
  n'y participe pas.
- Détail : [references/indexing-rules.md](references/indexing-rules.md).

## llms.txt — à ne plus survendre
Adoption ~10% des sites, et une étude Ahrefs sur 137 000 sites montre que
**97% des fichiers `llms.txt` n'ont reçu aucune requête** en mai 2026 : les
crawlers IA récupèrent le HTML directement. Google déclare explicitement ne
pas l'utiliser. Le créer coûte peu et ne nuit pas, mais le présenter comme un
levier GEO est faux, et il **n'a jamais été un mécanisme de contrôle d'accès**
(seul `robots.txt` en est un). Détail et sources :
[references/ai-crawlers.md](references/ai-crawlers.md).

## Agent Readiness — terrain émergent, pas un pilier
Cloudflare a lancé un score « Agent Readiness » (`isitagentready.com`) qui
mesure si un site est prêt pour l'interaction avec des agents IA autonomes
(MCP, Agent Skills, protocoles de commerce agentique). Adoption réelle
mesurée sur 200 000 domaines : Content Signals 4%, Markdown for Agents
3,9%, MCP/API catalogs réunis sur moins de 15 sites. À connaître, pas à
prioriser devant les leviers ci-dessus. Détail :
[references/agent-readiness.md](references/agent-readiness.md).

## Hygiène des données
Distinguer systématiquement donnée **mesurée** (Search Console, CrUX,
requête HTTP réelle) et **inférence/génération** (lecture de HTML, estimation,
bonne pratique générique). Ne jamais recycler une génération IA comme une
donnée vérifiée. [references/data-hygiene.md](references/data-hygiene.md).

## Limitation outillage connue
`curl`/`WebFetch` ne voient pas le schema injecté côté client (Yoast,
RankMath, AIOSEO l'injectent souvent en JS). Ne jamais conclure « pas de
schema » sur cette seule base : utiliser un navigateur
(`document.querySelectorAll('script[type="application/ld+json"]')`) ou le
Rich Results Test.

## Péremption
Ce domaine bouge vite : entre la première version de ce skill et cette
révision, Google a supprimé les rich results FAQ, publié une position
officielle sur les fichiers IA, et Cloudflare a annoncé un blocage par défaut
des crawlers IA. **Re-vérifier les affirmations datées avant de les
ressortir dans un audit** ; toute stat non sourcée ici a été retirée
volontairement plutôt que conservée sans preuve.

## Livrables
- `AUDIT_GEO.md` + `.json` — via `scripts/generate_report.py`.
- `CHANGELOG_GEO.md` — chaque modif et son objectif.
- Sortie de `validate_schema.py` avant de clore toute tâche schema.

## Références
| Fichier | Contenu |
|---|---|
| [references/cloudflare-ai-access.md](references/cloudflare-ai-access.md) | Blocage CDN des bots IA, diagnostic, correction |
| [references/ai-crawlers.md](references/ai-crawlers.md) | Liste des bots, robots.txt, llms.txt, Brave |
| [references/audit-framework.md](references/audit-framework.md) | Audit technique/on-page/E-E-A-T détaillé |
| [references/schema-templates.md](references/schema-templates.md) | Blocs JSON-LD prêts à coller, statut par type |
| [references/indexing-rules.md](references/indexing-rules.md) | Indexation : autorisé / interdit, IndexNow |
| [references/backlinks.md](references/backlinks.md) | Évaluation de liens, PBN, annuaires |
| [references/data-hygiene.md](references/data-hygiene.md) | Mesuré vs généré, péremption |
| [references/gsc-access.md](references/gsc-access.md) | Compte de service Search Console |
| [references/google-business-profile.md](references/google-business-profile.md) | API GBP, délai d'approbation, automatisable |
| [references/spam-policies.md](references/spam-policies.md) | Les 16 politiques anti-spam Google actuelles |
| [references/agent-readiness.md](references/agent-readiness.md) | Score Agent Readiness Cloudflare, adoption réelle |
| [references/checklist.md](references/checklist.md) | Ce que les scripts ne peuvent PAS vérifier |

## Scripts
| Script | Rôle | Accès requis |
|---|---|---|
| [check_ai_access.py](scripts/check_ai_access.py) | Accès réel des crawlers IA (détecte le blocage CDN) | aucun |
| [audit_site.sh](scripts/audit_site.sh) | Audit technique multi-URLs (curl) | aucun |
| [validate_schema.py](scripts/validate_schema.py) | Validation JSON-LD locale | aucun |
| [check_backlinks.sh](scripts/check_backlinks.sh) | dofollow/nofollow, ancres | aucun |
| [generate_sitemap.py](scripts/generate_sitemap.py) | sitemap.xml + robots.txt | aucun |
| [crux_report.py](scripts/crux_report.py) | Core Web Vitals terrain | clé API Google (gratuite) |
| [gsc_report.py](scripts/gsc_report.py) | Impressions/clics/positions réels | compte de service GSC |
| [indexnow_submit.py](scripts/indexnow_submit.py) | Soumission Bing/Yandex/Naver | clé IndexNow (auto-hébergée) |
| [generate_report.py](scripts/generate_report.py) | **Rapport consolidé** (technique + schema + hreflang + accès crawlers + CrUX + GSC) | tout optionnel sauf `--urls` |

`generate_report.py` accepte `--check-ai-access` et `--crux-key` en plus des
options GSC — la réciprocité hreflang est vérifiée automatiquement dès
qu'une page auditée en contient.
