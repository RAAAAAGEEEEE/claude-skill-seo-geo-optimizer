---
name: seo-geo-optimizer
description: >
  Audite puis corrige, dans le code d'un site, sa visibilité dans Google
  (dont AI Overviews, AI Mode, Discover, Actualités) et dans les moteurs de
  réponse IA (ChatGPT, Claude, Perplexity, Gemini, Copilot, Mistral) : accès
  réel des crawlers (robots.txt RFC 9309 et blocage CDN), indexabilité et
  extraits, JSON-LD, meta, structure, E-E-A-T, Core Web Vitals mesurés,
  Search Console, IndexNow. Chaque recommandation porte une source datée et
  une étiquette ESTABLISHED/SUPPORTED/CLAIMED. À utiliser pour « auditer le
  SEO/GEO », « pourquoi mon site n'est pas cité par ChatGPT/AI Overviews »,
  « vérifier robots.txt, sitemap, schema, llms.txt ». Ne pas confondre avec
  le skill `SEO` (prospection, digital PR, outreach via `/SEO`) : celui-ci
  audite et modifie le site courant, sans prospection ni outreach.
---

# SEO / GEO Optimizer

Version 2.0.0 — connaissances revues le **2026-09-27** (historique :
[CHANGELOG.md](CHANGELOG.md)). Au-delà de 3 mois, revérifier toute
affirmation datée avant de la ressortir.

## Principe
Deux fronts, un seul métier : Google dit lui-même que l'optimisation pour ses
fonctions IA « reste du SEO », et les autres moteurs de réponse s'appuient sur
des index de recherche. L'ordre ne se négocie pas :
**accès → indexation et extrait autorisé → contenu dans le HTML → preuves
vérifiables → balisage exact → performance**. Un site que les crawlers ne
peuvent pas lire a un plafond de zéro.

## Périmètre
- **Dans** : audit et modification du site courant (code, templates,
  robots.txt, sitemap, meta, JSON-LD, en-têtes), mesure via APIs gratuites.
- **Hors** : prospection, netlinking, digital PR, outreach → skill `SEO`
  (`/SEO`). Production massive de contenu → jamais (scaled content abuse).
- Sur un même projet : ce skill d'abord, `/SEO` ensuite.

## Quand l'utiliser
Audit SEO/GEO, site absent des réponses IA, doute sur robots.txt/CDN,
migration, ajout de schema, préparation d'un lancement, revue d'un
`llms.txt`/RSL. Pas pour rédiger du marketing (skill `copywriting`).

## Procédure (PLAN → FIX → VERIFY)

1. **Accès réel** — `python scripts/check_ai_access.py <url_importante>`.
   Sortie 1 = blocage, 2 = non concluant (le site ne répond pas 200 : ne rien
   conclure). Un crawler de recherche/citation bloqué est P0.
2. **Explorer** le repo : stack, rendu (SSR ou JS client), robots.txt,
   sitemaps, head/meta, JSON-LD, en-têtes, redirections, pages d'erreur.
3. **Auditer** — `python scripts/generate_report.py --urls urls.txt --out-prefix AUDIT_GEO --check-ai-access`
   (+ `--crux-key`, `--gsc-*` si accès). Inclure dans `urls.txt` : accueil,
   pages clés, une page de langue secondaire, une URL **inexistante** (doit
   répondre 404). Compléter avec [checklist.md](references/checklist.md)
   (réglages de comptes, jugement éditorial).
4. **PLAN** : prioriser P0/P1/P2 avec l'ordre ci-dessus, chaque point
   étiqueté et sourcé. **Attendre le GO** avant de coder.
5. **FIX** par lots, un diff à la fois. Décisions produit (ouvrir/fermer des
   crawlers, opt-out IA Google, migration d'URLs, désindexation) : exposer
   les options, **ne pas trancher**.
6. **VERIFY** : relancer les scripts sur les URLs modifiées ;
   `validate_schema.py` sur tout JSON-LD touché ; `python -m unittest discover -s tests`
   si un script du skill a changé. Pas de « terminé » sans sortie de script.

## Les leviers (détail dans les références)

| Levier | À retenir | Référence |
|---|---|---|
| Accès crawlers | Rôles engine / search / user / training / token ; `Google-Extended` et `Applebot-Extended` ne sont que des jetons ; plusieurs fetchers « utilisateur » ignorent robots.txt ; Cloudflare bloque Training+Agent par défaut sur les pages avec publicité depuis le 2026-09-15 | [ai-crawlers.md](references/ai-crawlers.md), [cloudflare-ai-access.md](references/cloudflare-ai-access.md) |
| Google IA | AI Overviews/AI Mode en France depuis le 2026-07-22 ; conditions : indexé + extrait autorisé + réglage Search Console « Search generative AI » sur Inclure ; rapports IA = impressions seulement | [google-ai-features.md](references/google-ai-features.md) |
| Technique / on-page | 404 et jamais 5xx sur une URL inconnue, 301/308 pour un déplacement définitif, pas de doublon de langue, canonical sur chaque page, contenu dans le HTML initial | [audit-framework.md](references/audit-framework.md) |
| Schema | Rich results FAQ supprimés le 2026-05-07 ; Dataset = Dataset Search seulement ; `WebSite` pour le nom du site ; pas d'étoiles auto-attribuées ; aucun schema « spécial IA » | [schema-templates.md](references/schema-templates.md) |
| Contenu citable | Preuves vérifiables (chiffres, sources, dates) ; fraîcheur réelle ; structure lisible ; pas de chunking artificiel | [evidence.md](references/evidence.md) |
| E-E-A-T / éditeur | Pas un facteur de classement en soi ; auteur désambiguïsé (`author.url`) ; politiques éditoriales exactes | [eeat-news.md](references/eeat-news.md) |
| Performance | LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 au p75 terrain (CrUX) | [audit-framework.md](references/audit-framework.md#vitesse--core-web-vitals) |
| Indexation | Google : sitemap exact (lastmod vrai) + Search Console ; Indexing API interdite hors JobPosting/BroadcastEvent ; IndexNow pour Bing & co, **clé à la racine** | [indexing-rules.md](references/indexing-rules.md) |
| Signaux « pour l'IA » | llms.txt, RSL, aipref, Content Signals : aucun fournisseur ne s'engage à les lire ; P2 au mieux | [licensing-signals.md](references/licensing-signals.md) |
| Agents | MCP, API catalog, WebMCP : marginal au 2026-09-27 | [agent-discovery.md](references/agent-discovery.md) |
| Liens | Évaluer, pas acquérir ; `sponsored`/`ugc`/`nofollow` = indications | [backlinks.md](references/backlinks.md), [spam-policies.md](references/spam-policies.md) |
| Local | API GBP : fiche validée depuis 60+ jours, approbation manuelle | [google-business-profile.md](references/google-business-profile.md) |

## Niveaux de preuve
- **ESTABLISHED** (doc officielle, déclaration du fournisseur sur son
  produit), **SUPPORTED** (étude indépendante avec données), **CLAIMED**
  (vendeur ou blog, y compris étude de vendeur à méthode publiée). Un
  CLAIMED ne fonde jamais seul une priorité.
- Chaque constat d'audit : **mesuré** (requête HTTP, CrUX, Search Console),
  **inféré** (HTML, code) ou **hypothèse**. Détail :
  [data-hygiene.md](references/data-hygiene.md).

## Replis et erreurs
- Schema injecté en JavaScript (Yoast, RankMath...) : `curl` ne le voit pas ;
  conclure avec un navigateur ou le Rich Results Test, jamais « pas de schema ».
- `check_ai_access.py` teste avec des user-agents simulés depuis votre
  machine : un 403 prouve une règle par user-agent, un 200 ne prouve pas que
  le vrai bot passe. Confirmer dans les journaux ou le tableau de bord CDN.
- CrUX sans données = trafic insuffisant, pas un problème de performance :
  mesure labo étiquetée comme telle.
- Pas d'accès Search Console / Bing Webmaster Tools : le dire, ne pas
  extrapoler une mesure de citation.
- Page en 403/JS lors d'une vérification de source : noter « non vérifié ».

## Sécurité et confidentialité
- Par défaut, les scripts ne font que des **GET publics** vers le site
  audité. Rien d'autre ne sort sans option explicite : `--crux-key` (clé
  Google en paramètre d'URL vers l'API CrUX), `--gsc-service-account`
  (jeton OAuth vers l'API Search Console), `indexnow_submit.py` sans
  `--dry-run` (URLs envoyées à api.indexnow.org et partagées avec tous les
  moteurs participants : **action externe, confirmation requise**).
- Clés et fichiers de compte de service : hors du dépôt, jamais affichés
  dans un rapport ni un log.
- Aucune modification de compte (Search Console, CDN, GBP) par ce skill :
  il liste les réglages, le propriétaire les change.

## Exemples d'invocation
- « Audite le SEO/GEO de ce site et propose un plan » → procédure complète.
- « Pourquoi Perplexity ne nous cite jamais ? » → étape 1, puis
  [ai-crawlers.md](references/ai-crawlers.md).
- « Ajoute le schema produit » → [schema-templates.md](references/schema-templates.md),
  puis `validate_schema.py`.

## Exemple de sortie (réelle, site anonymisé, 2026-09-27)
```
### https://example.com/
- Redirections : 307 https://example.com/fr
- **redirection temporaire 307 vers https://example.com/fr : utiliser 301/308 si le deplacement est definitif**

### https://example.com/fr/donnees
- **canonical manquant**
- schema : ...Dataset - sert uniquement a Dataset Search, pas a Google Search (05/11/2025)

### https://example.com/fr/robots/nexiste-pas
- **HTTP 500 : erreur serveur (une URL inconnue doit repondre 404/410, jamais 5xx ; des 5xx repetes ralentissent le crawl)**
```

## Livrables
- `AUDIT_GEO.md` + `AUDIT_GEO.json` (`generate_report.py`), complétés à la
  main par la checklist et les priorités P0/P1/P2 étiquetées.
- `CHANGELOG_GEO.md` dans le projet audité : chaque modification et son but.
- Sortie de `validate_schema.py` avant de clore une tâche schema.

## Scripts
| Script | Rôle | Accès requis |
|---|---|---|
| [check_ai_access.py](scripts/check_ai_access.py) | robots.txt (RFC 9309) + accès HTTP par crawler vs navigateur | aucun |
| [generate_report.py](scripts/generate_report.py) | Rapport consolidé (redirections, noindex/nosnippet, meta, canonical, lang, schema, hreflang, crawlers, CrUX, GSC) | optionnel |
| [audit_site.sh](scripts/audit_site.sh) | Passe rapide curl multi-URLs | aucun |
| [validate_schema.py](scripts/validate_schema.py) | JSON-LD vs exigences Google, types retirés, avis auto-attribués | aucun |
| [generate_sitemap.py](scripts/generate_sitemap.py) | sitemap.xml conforme + robots.txt (`--ai-policy open\|search-only`) | aucun |
| [indexnow_submit.py](scripts/indexnow_submit.py) | IndexNow avec contrôle de la clé et de sa portée | clé auto-hébergée |
| [crux_report.py](scripts/crux_report.py) | Core Web Vitals terrain | clé API Google gratuite |
| [gsc_report.py](scripts/gsc_report.py) | Search Console (web, discover, googleNews, news, image, video) | compte de service |
| [check_backlinks.sh](scripts/check_backlinks.sh) | Liens suivis vs nofollow/sponsored/ugc, ancres | aucun |

Modules partagés : [ai_bots.py](scripts/ai_bots.py) (catalogue des
crawlers, source unique avec [ai-crawlers.md](references/ai-crawlers.md)),
[robotstxt.py](scripts/robotstxt.py), [htmlsignals.py](scripts/htmlsignals.py).
Tests hors ligne : `python -m unittest discover -s tests`.

## Installation
Personnelle : `~/.claude/skills/seo-geo-optimizer/`. Par projet :
`.claude/skills/seo-geo-optimizer/`. Python 3.10+, bibliothèque standard ;
`pip install google-auth requests` uniquement pour `gsc_report.py`. Voir
[README.md](README.md).
