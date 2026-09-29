# SEO/GEO automatisable : ce qu'un script ou un agent planifié peut faire seul

Revu le 2026-09-28. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
« maj » = date « Last updated » de la page ; « consulté » = page sans date,
lue le 2026-09-28. Les URLs de fichiers JSON ont été téléchargées ce jour-là
(HTTP 200).

**Règle.** Automatiser la **mesure**, la **détection** et la **préparation**
d'un correctif. Ne jamais automatiser la **publication** de contenu, de
liens ou de balisage sans relecture : c'est précisément ce que visent les
politiques anti-spam de Google (dernière section).

## Classement pour un petit site (valeur / effort)

| # | Technique | Ce que le skill fournit | Niveau |
|---|---|---|---|
| 1 | Audit technique complet planifié, diff avec le passage précédent | `run_audit.py` | ESTABLISHED (règles Google) |
| 2 | IndexNow des seules URLs nouvelles ou modifiées, au déploiement | `run_audit.py --indexnow-submit`, `indexnow_submit.py` | ESTABLISHED |
| 3 | Sitemap (et flux RSS/Atom) avec un `lastmod` exact | `generate_sitemap.py`, contrôle dans `run_audit.py` | ESTABLISHED |
| 4 | Analyse des journaux serveur : crawlers réels, statuts, usurpations, couverture du sitemap | **`crawler_logs.py`** (nouveau) | ESTABLISHED (méthode de vérification) |
| 5 | Search Console : performances quotidiennes, données horaires, alertes d'écart | `gsc_report.py`, module de `run_audit.py` | ESTABLISHED |
| 6 | URL Inspection API sur les pages clés (canonical retenu, couverture, dernier crawl) | non fourni ; quota 2 000/jour/site | ESTABLISHED |
| 7 | JSON-LD généré côté serveur depuis la base, avec contrôle « balisé = visible » | `validate_schema.py`, `glossary_check.py build` | ESTABLISHED |
| 8 | Orphelines et occasions de liens internes, **validées par un humain** | `linkgraph.py`, **`glossary_check.py audit --site`** | ESTABLISHED (principes) |
| 9 | Bing Webmaster API : requêtes, pages, crawl | non fourni | ESTABLISHED |
| 10 | Panel de questions posées aux API de recherche IA (OpenAI, Perplexity, Anthropic) | non fourni : payant, indicateur approché | voir « Citations IA » |

## 1. APIs de suivi technique

| Affirmation | Niveau | Source (date) |
|---|---|---|
| Search Analytics : dimension `hour` avec `dataState=HOURLY_ALL`, jusqu'à 10 jours de données horaires | ESTABLISHED | [Google](https://developers.google.com/search/blog/2025/04/san-hourly-data) (2025-04-09) |
| `type` = web, image, video, news, googleNews, discover ; **aucun type IA** (AI Overviews et AI Mode sont comptés dans web) | ESTABLISHED | [référence](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) (maj 2026-08-11) |
| Quotas : Search Analytics 1 200 req/min par site et par utilisateur ; URL Inspection 600/min et 2 000/jour par site | ESTABLISHED | [limits](https://developers.google.com/webmaster-tools/limits) (maj 2025-08-28) |
| URL Inspection API : version indexée seulement (pas de test en direct) ; renvoie couverture, état robots.txt, dernier crawl, canonical Google et canonical déclaré, sitemaps, rich results | ESTABLISHED | [inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect) (maj 2024-07-23) |
| Pas d'API pour Crawl Stats ni pour le rapport « Generative AI performance » (impressions seules, export manuel) | ESTABLISHED (absence) | [référence API](https://developers.google.com/webmaster-tools/v1/api_reference_index) ; [Google](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports) (2026-06-03) |
| Bing Webmaster API : GetQueryStats, GetPageStats, GetCrawlStats, GetCrawlIssues, GetUrlInfo, SubmitUrlBatch, GetUrlSubmissionQuota… ; **aucune méthode « AI Performance »** | ESTABLISHED | [Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet) (consulté) |
| Bing AI Performance : citations Copilot, grounding queries, Citation Share ; interface seulement | ESTABLISHED | [Bing](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview) (2026-02-10) ; [Bing](https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/) (2026-06-16) |
| IndexNow : 10 000 URLs par POST ; soumettre les URLs nouvelles, modifiées ou supprimées ; Google ne participe pas | ESTABLISHED | [documentation](https://www.indexnow.org/documentation), [searchengines.json](https://www.indexnow.org/searchengines.json) (consultés) |
| Indexing API : JobPosting et BroadcastEvent seulement ; abus = perte d'accès | ESTABLISHED | [quickstart](https://developers.google.com/search/apis/indexing-api/v3/quickstart) (maj 2026-07-16) |

## 2. Journaux serveur : vérifier les crawlers

Un crawl simulé ne dit pas qui vient vraiment. Le journal le dit, à
condition de vérifier l'IP : n'importe qui peut écrire « Googlebot » dans
son user-agent.

| Affirmation | Niveau | Source (date) |
|---|---|---|
| Google : DNS inverse puis direct (`googlebot.com`, `google.com`, `googleusercontent.com`), ou comparaison aux plages JSON | ESTABLISHED | [verify requests](https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests) (maj 2026-03-20) |
| Plages Google : `common-crawlers.json`, `special-crawlers.json`, `user-triggered-fetchers.json`, `user-triggered-fetchers-google.json`, `user-triggered-agents.json` sous `/static/crawling/ipranges/` ; l'ancien `googlebot.json` sera redirigé | ESTABLISHED | [Google](https://developers.google.com/search/blog/2026/03/crawler-ip-ranges) (2026-03-31) |
| Google-Agent teste Web Bot Auth (RFC 9421, en-tête `Signature-Agent`) ; seule une partie des requêtes est signée, garder l'IP en repli | ESTABLISHED | [web bot auth](https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth) (maj 2026-05-04) |
| Listes JSON publiées : OpenAI (`searchbot`, `gptbot`, `chatgpt-user`, `adsbot`), Perplexity (`perplexitybot`, `perplexity-user`), Anthropic (`claude.com/crawling/bots.json`), Apple (`applebot.json`), Bing (`bingbot.json`, daté de 2024-01-03), DuckDuckGo, Common Crawl, Mistral (`mistralai-user-ips`, `mistralai-index-ips`) | ESTABLISHED | pages « bots » des fournisseurs (consultées) ; URLs exactes dans `scripts/crawler_logs.py` |
| Meta : ni liste JSON ni méthode de vérification ; Amazon : listes en pages HTML | ESTABLISHED (absence) | [Meta](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/), [Amazon](https://developer.amazon.com/amazonbot) (consultés) |
| Anthropic déconseille de bloquer ses crawlers par IP (les plages changent) | ESTABLISHED | [Anthropic](https://support.claude.com/en/articles/8896518) (maj 2026-04-07) |
| Des 5xx ou des 429 ralentissent le crawl de Google ; un robots.txt en 5xx ou 429 arrête le crawl | ESTABLISHED | [crawl budget](https://developers.google.com/crawling/docs/crawl-budget) ; [spec robots.txt](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec) (maj 2026-08-31) |
| Le rapport Crawl Stats de Search Console ne compte pas toutes les requêtes et peut différer des journaux ; pas d'API | ESTABLISHED | [aide](https://support.google.com/webmasters/answer/9679690) (consulté) |

`crawler_logs.py` lit un journal (format *combined* ou JSON lines), compte
les requêtes par crawler, vérifie les IP contre les listes ci-dessus et
signale : 5xx/429 servis aux crawlers, robots.txt hors 200, usurpations,
404 les plus demandés, URLs du sitemap jamais récupérées. **Aucune adresse
IP n'est écrite** dans la sortie. Le DNS inverse et Web Bot Auth ne sont pas
faits (limite documentée).

Les hits de `ChatGPT-User`, `Perplexity-User`, `Claude-User` ou `Google-Agent`
sont les seules traces **mesurées** qu'une réponse IA est allée chercher une
page du site. Ce n'est pas une citation, mais c'est un signal first-party.

## 3. Maillage, entités, pages programmatiques

| Affirmation | Niveau | Source (date) |
|---|---|---|
| Liens en `<a href>` ; au moins un lien vers chaque page importante ; ancres descriptives ; bourrer les ancres de mots-clés est du spam | ESTABLISHED | [links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) (maj 2025-12-10) |
| Google n'a publié aucune doc sur le maillage interne **automatisé** | ESTABLISHED (absence) | recherche du 2026-09-28 |
| JSON-LD généré dynamiquement (serveur ou JS) : lu par Google, à condition de décrire le contenu visible ; sinon action manuelle possible (perte des rich results) | ESTABLISHED | [intro](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data) (maj 2025-12-10) ; [policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) (maj 2026-07-10) |
| `Organization` et `sameAs` sur l'accueil ou la page À propos, pas sur chaque page | ESTABLISHED | [Organization](https://developers.google.com/search/docs/appearance/structured-data/organization) (maj 2026-09-08) |
| Contenu généré par IA admis s'il apporte de la valeur ; soigner l'exactitude des titles, meta, données structurées et textes alt générés | ESTABLISHED | [contenu IA](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) (maj 2025-12-10) |
| Une page par variante ou par sous-requête *fan-out* pour manipuler les réponses IA = *scaled content abuse* | ESTABLISHED | [guide IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (maj 2026-07-10) |
| Google ne donne aucun exemple officiel de pages programmatiques « légitimes » | ESTABLISHED (absence) | idem |

Pages programmatiques sans abus, en pratique : une page n'existe que si la
base contient des **données propres** à cette page (fiche produit, robot,
commune avec des chiffres réels). Pas de page si la donnée manque ;
`noindex` tant qu'elle est vide ; jamais de texte de remplissage généré pour
varier. Ce critère est une lecture des politiques Google, pas une règle
écrite par Google.

Glossaire généré depuis les données du site : voir [glossary.md](glossary.md).

## 4. Fraîcheur et flux

| Affirmation | Niveau | Source (date) |
|---|---|---|
| `lastmod` utilisé s'il est exact de façon constante et vérifiable, pour un changement significatif ; RSS 2.0 et Atom 1.0 acceptés comme sitemaps ; WebSub recommandé pour les flux | ESTABLISHED | [build sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) (maj 2026-07-08) |
| Date visible et `datePublished`/`dateModified` cohérentes ; pas de date future | ESTABLISHED | [publication dates](https://developers.google.com/search/docs/appearance/publication-dates) (maj 2025-12-10) |
| Redemander le crawl d'une URL plusieurs fois ne l'accélère pas | ESTABLISHED | [recrawl](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl) (maj 2025-12-10) |
| Changer la date sans changer le contenu est déconseillé | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content) (2025-07-28) |

## 5. Citations IA : ce qui se mesure vraiment

| Source | Ce qu'elle donne | Automatisable ? | Niveau |
|---|---|---|---|
| Search Console « Generative AI performance » | Impressions AI Overviews, AI Mode, Discover ; pas de clics | Non : interface et export manuel | ESTABLISHED |
| Bing « AI Performance » | Citations Copilot et résumés Bing, grounding queries, Citation Share | Non : interface | ESTABLISHED |
| Journaux serveur | Hits des fetchers « utilisateur » (ChatGPT-User, Perplexity-User…) | **Oui** (`crawler_logs.py`) | mesuré |
| Analytics (référents) | Visites venant de chatgpt.com, perplexity.ai… | Oui | mesuré ; `utm_source=chatgpt.com` **non vérifié** à la source |
| API OpenAI `web_search` | Annotations `url_citation` (URL, titre, position) et liste des sources ; citations « clearly visible and clickable » à l'affichage | Oui, payant | ESTABLISHED ([doc](https://developers.openai.com/api/docs/guides/tools-web-search), consulté) |
| API Perplexity Sonar | `citations[]` et `search_results[]` (url, date, snippet) | Oui, payant | ESTABLISHED ([doc](https://docs.perplexity.ai/api-reference/chat-completions-post), consulté) |
| API Anthropic `web_search` | Citations avec url, titre, extrait cité ; filtres de domaines | Oui, payant | ESTABLISHED ([doc](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), consulté) |
| API Gemini, grounding Google Search | `groundingMetadata`, `url_citation` | **Interdit pour ce usage** : les conditions défendent de « cache, frame, syndicate, resell, analyze » les résultats et de collecter les liens « using programmatic or automated means » | ESTABLISHED ([conditions](https://ai.google.dev/gemini-api/terms), maj 2026-04-28) |
| Scraper Google (AI Overviews, AI Mode) | — | **Interdit** : conditions Google (accès automatisé contraire à robots.txt, `Disallow: /search`) et politique « machine-generated traffic » | ESTABLISHED ([conditions](https://policies.google.com/terms), en vigueur 2026-07-30 ; [spam policies](https://developers.google.com/search/docs/essentials/spam-policies), maj 2026-08-28) |
| Outils tiers (Profound, Semrush AI Visibility, Ahrefs Brand Radar, Otterly, Peec AI) | Taux de mention sur panels de prompts | Oui, payant | CLAIMED (pages des éditeurs, consultées) |

Lecture :
- Une réponse d'API n'est **pas** la réponse que voit un utilisateur de
  ChatGPT, de Perplexity ou d'AI Overviews : autre modèle, autres réglages,
  pas d'historique. Aucun fournisseur ne dit le contraire ; des utilisateurs
  signalent des écarts (CLAIMED). Un panel par API est un **indicateur
  approché**, à présenter comme tel.
- Les réponses varient d'une exécution à l'autre (9,2 % d'URLs identiques
  sur 3 exécutions AI Mode, SE Ranking, CLAIMED méthode publiée) : mesurer
  une tendance sur plusieurs passages, jamais un passage isolé.
- Vérifier les conditions du fournisseur avant de construire un suivi : un
  usage interdit (Gemini, Google) ne devient pas acceptable parce qu'il est
  automatisé.
- Le relevé manuel de Stéphane Delgado (D1, D4 dans
  [french-practitioners.md](french-practitioners.md)) reste la méthode la
  plus proche de l'expérience réelle, au prix de la reproductibilité.

## 6. Veille des mentions (digital PR)

Hors périmètre de modification de ce skill (le skill `seo` s'occupe de la
prospection). Sources automatisables, à titre d'information :

| Source | Ce qu'elle offre | Niveau |
|---|---|---|
| [GDELT DOC 2.0](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | Articles de presse sur 3 mois glissants, 65 langues, JSON ou RSS ; limitation de débit (429 constaté) | ESTABLISHED (doc éditeur) |
| [Common Crawl](https://index.commoncrawl.org/collinfo.json) | Index CDX gratuit ; dernier au 2026-09-28 : CC-MAIN-2026-39 (collecte 2026-09-04 → 2026-09-17) | ESTABLISHED |
| Google Alerts | Email documenté ; la sortie RSS n'est pas dans l'aide | ESTABLISHED (email) ; RSS non vérifié |

Les mentions de marque corrèlent avec la visibilité dans les AI Overviews
(CLAIMED, méthode publiée, voir [evidence.md](evidence.md)) : les suivre a
du sens, les fabriquer est du *link spam*.

## 7. Ce que Google interdit quand on automatise

Source : [spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
(maj 2026-08-28), sauf mention. Tout est ESTABLISHED.

- Requêtes automatisées vers Google et scraping des résultats (voir aussi
  les [conditions](https://policies.google.com/terms)).
- *Scaled content abuse* : beaucoup de pages générées d'abord pour classer,
  quel que soit l'outil (IA, scraping, assemblage, traduction automatique).
- *Link spam* : « Using automated programs or services to create links to
  your site ».
- *Cloaking*, redirections trompeuses, *doorways*.
- Abus de domaine expiré et de réputation de site (règle modifiée pour
  l'EEE le [2026-08-28](https://developers.google.com/search/blog/2026/08/update-site-reputation-policy)).
- *Back button hijacking*, sanctionné depuis le 2026-06-15
  ([Google](https://developers.google.com/search/blog/2026/04/back-button-hijacking), 2026-04-13).
- Indexing API hors JobPosting/BroadcastEvent ([quickstart](https://developers.google.com/search/apis/indexing-api/v3/quickstart), maj 2026-07-16).
- Données structurées trompeuses ou invisibles ([policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies), maj 2026-07-10).
- Dates fausses ou futures ([publication dates](https://developers.google.com/search/docs/appearance/publication-dates), maj 2025-12-10).

## Non vérifié (2026-09-28)

- Quota réel de l'API de soumission d'URL Bing (aide rendue en JavaScript).
- Ajout de `utm_source=chatgpt.com` par ChatGPT (aide OpenAI en 403).
- Programme éditeurs de Perplexity (403).
- Déclarations de Google sur le maillage interne automatisé (sources
  secondaires seulement).
- Aucune étude indépendante (SUPPORTED) trouvée sur ces techniques.
