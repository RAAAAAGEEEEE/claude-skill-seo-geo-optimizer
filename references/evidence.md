# Registre des preuves GEO : études, déclarations, croyances démenties

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
À consulter avant d'écrire une recommandation « de contenu pour l'IA » dans un
audit : si l'affirmation n'est pas ici ou dans une autre référence datée, elle
est à sourcer ou à retirer.

## Ce qui est établi (déclarations des moteurs sur eux-mêmes)

| Déclaration | Source (date) |
|---|---|
| Google : optimiser pour l'IA générative « reste du SEO » ; les fonctions IA récupèrent les pages via les systèmes de classement de Search ; ignorer chunking, llms.txt, mentions inauthentiques ; pas de schema spécial ; valeur = contenu original, non standardisé | [guide Google](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (maj 2026-07-10) |
| Google : « E-E-A-T itself isn't a specific ranking factor » ; signatures d'auteur fortement encouragées ; pas de nombre de mots préféré ; les notes des évaluateurs n'agissent pas directement sur le classement | [helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) (maj 2025-12-10) |
| Microsoft : les réponses IA découpent les pages ; titres clairs, réponses directes, listes, tableaux, Q/R ; contenu caché (onglets), PDF et texte dans l'image mal lus | [Microsoft, 2025-10-08](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers) |
| Bing : l'index choisit des informations pour étayer une réponse (qualité de la preuve, provenance, fraîcheur) | [Bing, 2026-05-06](https://blogs.bing.com/search/May-2026/Evolving-role-of-the-index-From-ranking-pages-to-supporting-answers) |
| OpenAI, Anthropic, Perplexity : aucun critère de sélection des sources publié ; seuls les crawlers et robots.txt sont documentés | pages crawlers (consultées 2026-09-27) |

Tout est **ESTABLISHED**. Google et Bing divergent sur la forme (Google : ne
pas réécrire pour l'IA ; Bing : structurer en blocs) mais convergent sur le
fond : contenu visible dans le HTML, clair, original, à jour.

## Ce que mesurent les études

| Constat | Étiquette | Source (date) |
|---|---|---|
| Ajouter citations, statistiques et sources augmente la visibilité dans un moteur **simulé** (jusqu'à ~40 %) ; bourrage de mots-clés inutile ; les sources mal classées gagnent le plus | SUPPORTED (KDD 2024) | [Aggarwal et al.](https://arxiv.org/abs/2311.09735) (2024-06-28) |
| Les moteurs IA citent surtout des médias tiers (« earned ») plutôt que le site de la marque | SUPPORTED (préprint) | [arXiv 2509.08919](https://arxiv.org/html/2509.08919) (2025-09-10) |
| Avec un résumé IA Google : 8 % de clic sur un résultat contre 15 % ; 1 % sur une source du résumé | SUPPORTED | [Pew](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/) (2025-07-22) |
| Attribution fautive de l'actualité par les moteurs IA dans > 60 % des cas ; près de la moitié des réponses d'assistants sur l'actualité ont un problème significatif | SUPPORTED | [CJR](https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php) (2025-03-06) ; [EBU/BBC](https://www.ebu.ch/research/open/report/news-integrity-in-ai-assistants) (2025-10-21) |
| Pages citées dans AI Overviews présentes dans le top 10 : 76 % (07/2025) puis ~38 % (03/2026) ; AI Mode ~14 % ; ChatGPT ~10 %, Perplexity ~65 % | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/ai-overview-citations-top-10/) (2026-03-02) ; [SE Ranking](https://seranking.com/blog/ai-mode-research/) (2025-08-29) ; [Ahrefs](https://ahrefs.com/blog/chatgpt-google-citations/) (2025-09-03) |
| Mentions de marque sur le web plus corrélées à la visibilité AI Overviews (0,664) que les backlinks (0,218) — corrélation, pas causalité | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/ai-overview-brand-correlation/) (2025-05-26) |
| Contenus cités plus récents que l'organique (sauf AI Overviews) ; changer la date sans changer le contenu est déconseillé | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content) (2025-07-28) |
| Ajouter du JSON-LD n'augmente pas les citations (1 885 pages contre 4 000 témoins) | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/schema-ai-citations/) (2026-05-11) |
| llms.txt : 97 % des fichiers jamais demandés (mai 2026) ; aucun lien avec les citations | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/llmstxt-study/) (2026-06-15) ; [SE Ranking](https://seranking.com/blog/llms-txt/) (2025-11-07) |
| Citations AI Mode instables : 9,2 % des URLs identiques sur 3 exécutions | CLAIMED, méthode publiée | [SE Ranking](https://seranking.com/blog/ai-mode-research/) (2025-08-29) |
| CTR organique −61 % sur requêtes avec AI Overview (2024-2025), remontée partielle début 2026 ; une autre étude ne voit pas de hausse du zéro clic | CLAIMED, méthode publiée — **études en conflit** | [Seer](https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update) (2026-04-24) ; [Semrush](https://www.semrush.com/blog/semrush-ai-overviews-study/) (2025-12-15) |

Traduction opérationnelle, sans surinterpréter :
1. **Être récupérable d'abord** : accès crawler, indexation, extrait autorisé,
   contenu dans le HTML initial. Sans cela, rien d'autre ne compte.
2. **Des preuves vérifiables dans le texte** (chiffres, citations, sources,
   dates de vérification) : seul levier de contenu appuyé par une étude
   causale, en cadre simulé.
3. **Exister ailleurs que chez soi** : mentions et reprises par des tiers
   (le rôle du skill `SEO`, pas de celui-ci).
4. **Fraîcheur réelle** : mettre à jour le contenu, pas seulement la date.
5. Le reste (formats de page, longueur, schema « pour l'IA ») n'est pas
   démontré : le présenter comme hypothèse. Parts de citation par format
   et conflits entre études : [content-formats.md](content-formats.md)
   (2026-09-28).

## Croyances répandues démenties ou non soutenues

| Croyance | Réalité documentée |
|---|---|
| « llms.txt aide à être cité » | Google Search l'ignore ; aucun fournisseur ne dit le lire ; pas de corrélation mesurée |
| « Il faut un schema spécial pour l'IA » / « le FAQ schema fait citer » | Non (Google) ; pas d'effet mesuré ; rich result FAQ supprimé le 2026-05-07 |
| « Google-Extended retire des AI Overviews » | Non ; réglage Search Console ou `nosnippet` |
| « Bloquer GPTBot retire de ChatGPT search » | Non ; c'est `OAI-SearchBot` |
| « Tous les bots IA respectent robots.txt » | Plusieurs fetchers « utilisateur » ont des exceptions documentées |
| « Il faut découper le contenu en morceaux pour l'IA » | Google : à ignorer |
| « AEO/GEO est une discipline à part » | Google : « still SEO » |
| « E-E-A-T est un facteur de classement » / « le nombre de mots compte » | Démenti par Google |
| « Être n°1 = être cité » | Recouvrement partiel et en baisse (études de vendeurs) |
| « 75 % des sites internationaux ont une erreur hreflang (étude 2026) » | Étude SEMrush **2017** ; Ahrefs 2023 : 67 % en comptant l'absence de `x-default`, que Google n'exige pas (CLAIMED, méthode publiée) |
| « ~65 % de recherches zéro clic en 2026 » | Chiffre 2020 ; 68,01 % US début 2026 (CLAIMED, méthode publiée) |
| « Le seuil LCP est passé à 2,0 s » | Toujours 2,5 s |
| « Un glossaire fait citer par les IA (3 à 5 fois plus) » | Aucune étude avec méthode ; effet non démontré ([glossary.md](glossary.md), 2026-09-28) |
| « On peut suivre ses citations AI Overviews en scrapant Google, ou via le grounding Gemini » | Interdit par les conditions de Google et de l'API Gemini ([automation.md](automation.md), 2026-09-28) |
| « Les IA respectent RSL / Content Signals / aipref » | Aucun engagement public |
| « Les AI Overviews sont invisibles dans Search Console » | Type Web + rapport Generative AI (impressions) |

Chiffres de « gain de citation par type de schema » repris par les blogs SEO :
aucun ne repose sur des données primaires publiées (vérifié le 2026-09-27).
Ne pas les réintroduire.
