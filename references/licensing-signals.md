# Fichiers et signaux « pour l'IA » : llms.txt, RSL, aipref, Content Signals

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Point commun : **aucun grand fournisseur d'IA ne s'engage publiquement à lire
ou respecter ces signaux** au 2026-09-27 (vérifié sur les pages crawlers
d'OpenAI, Anthropic, Perplexity : ESTABLISHED par absence). Seul `robots.txt`
est honoré, et seul le serveur/CDN contrôle réellement l'accès. Ces signaux
coûtent peu ; ils ne remplacent aucun levier.

## llms.txt

| Constat | Étiquette | Source |
|---|---|---|
| Proposé le 2024-09-03 (Jeremy Howard) ; page « v2 » modifiée le 2026-08-10, toujours ouverte aux commentaires, pas de standard formel | ESTABLISHED | [llmstxt.org](https://llmstxt.org/) |
| Google Search l'ignore ; le créer « ne nuit ni n'aide » Search (formulation assouplie le 2026-06-15) | ESTABLISHED | [guide Google](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (maj 2026-07-10) |
| Chrome Lighthouse a un audit llms.txt (catégorie « Agentic Browsing ») : signale les erreurs serveur, 404 = N/A | ESTABLISHED | [Chrome](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt) (2026-05-05) |
| Ahrefs, 137 210 domaines : 28 % publient un llms.txt, **97 % de ces fichiers n'ont reçu aucune requête en mai 2026** ; parmi les requêtes restantes, bots IA 19,5 %, outils SEO 21,7 % | CLAIMED, méthode publiée (échantillon = clients Ahrefs Web Analytics) | [Ahrefs](https://ahrefs.com/blog/llmstxt-study/) (2026-06-15) |
| SE Ranking, 300 000 domaines : adoption 10,13 % ; aucun lien entre présence du fichier et citations par les LLM | CLAIMED, méthode publiée | [SE Ranking](https://seranking.com/blog/llms-txt/) (2025-11-07) |
| OpenAI, Anthropic, Perplexity publient un llms.txt pour **leur propre** documentation ; aucun ne dit que ses crawlers lisent celui des autres | ESTABLISHED | pages crawlers des trois (consultées 2026-09-27) |
| Mintlify le génère automatiquement pour les sites de documentation | ESTABLISHED | [Mintlify](https://www.mintlify.com/docs/ai/llmstxt) |

Usage résiduel légitime : documentation technique lue par des outils de
code (Claude Code apparaît dans les journaux Ahrefs). Pour un site vitrine,
SaaS ou commerce : P2 au mieux, jamais présenté comme levier de citation, et
**jamais** comme contrôle d'accès.

## RSL (Really Simple Licensing)

- RSL 1.0 publié le 2025-12-10, statut « Recommendation » — ESTABLISHED
  ([spec](https://rslstandard.org/rsl)).
- Déclaration : ligne `License: <URL>` dans robots.txt, en-tête
  `Link: <url>; rel="license"; type="application/rsl+xml"`, balise HTML,
  flux RSS/Atom, ou `/license.xml`.
- **Vocabulaire exact** (erreurs fréquentes) :
  - `<permits|prohibits type="usage">` : `all`, `ai-all`, `ai-train`,
    `ai-input`, `ai-index`, `search`. Les anciens jetons `train-ai`,
    `ai-summarize` ne sont **pas** valides.
  - `type="user"` : `commercial`, `non-commercial`, `education`,
    `government`, `personal` (pas de `all`).
  - `<content url="...">` : un **chemin** au sens RFC 9309 (`/api/*`),
    pas une URL absolue, sauf licence embarquée dans le contenu lui-même.
  - `<payment type="...">` : `purchase`, `subscription`, `training`,
    `crawl`, `use`, `contribution`, `attribution`, `free`. Une licence
    Creative Commons s'exprime par
    `<payment type="attribution"><standard>https://creativecommons.org/licenses/by/4.0/</standard></payment>`.
  - `<terms>`, `<copyright>`, `<schema>` sont enfants de `<content>`, pas de
    `<license>` ; `<metadata>` et `<description>` n'existent pas.
- Soutiens revendiqués (éditeurs, Cloudflare, Akamai, Fastly) : CLAIMED
  (liste du RSL Collective). **Aucune entreprise d'IA** affichée comme
  s'engageant à le respecter (ESTABLISHED par absence, 2026-09-27).

## IETF aipref (préférences d'usage IA)

- `draft-ietf-aipref-vocab-08` (2026-09-14) : catégories `train-ai`,
  `ai-use`, `search` ; le brouillon précise qu'il ne reflète pas un
  consensus. `draft-ietf-aipref-attach-05` (2026-08-19) : règle
  `Content-Usage` dans robots.txt et en-tête HTTP `Content-Usage`.
  ESTABLISHED ([datatracker](https://datatracker.ietf.org/wg/aipref/documents/)).
- Jalon IESG du 2026-08-31 manqué. Aucun crawler ne documente le support.
  À surveiller, pas à déployer comme levier.

## Content Signals (Cloudflare)

- `Content-Signal: search=yes, ai-input=yes, ai-train=no` dans robots.txt
  (2025-09-24) ; champ `use=immediate|reference|full` ajouté le 2026-07-01.
- Cloudflare dit lui-même que ce sont des préférences, pas une protection
  technique ; aucun engagement d'une entreprise d'IA annoncé. ESTABLISHED
  ([blog](https://blog.cloudflare.com/content-signals-policy/)).
- Adoption : 4 % des 200 000 domaines les plus visités (scan Cloudflare,
  2026-04-17 — CLAIMED, méthode publiée, vendeur de la fonction).

## Pay per crawl / Pay Per Use

HTTP 402 + en-tête `crawler-price`, requêtes signées Web Bot Auth, bêta
fermée ; « évolue vers Pay Per Use » (paiement à la valeur, partenaires
You.com et Ceramic.ai) depuis le 2026-07-01. Détail :
[cloudflare-ai-access.md](cloudflare-ai-access.md). Sujet d'éditeur qui
monétise, pas de site qui cherche la visibilité.

## Markdown pour agents

- Cloudflare « Markdown for Agents » (2026-02-12, plans payants) convertit le
  HTML si la requête envoie `Accept: text/markdown`.
- Une étude sur un seul site (44 jours, 1 421 requêtes Markdown ; ~35 %
  d'user-agents Claude) montre que certains agents le demandent — SUPPORTED
  (indépendant), mais un seul site ([Suganthan, 2026-04-19](https://suganthan.com/blog/cloudflare-markdown-for-agents/)).
- Google Search n'en a pas besoin (guide Google). Utile éventuellement pour
  des agents ; jamais prioritaire devant l'accès, l'indexation et le contenu.
