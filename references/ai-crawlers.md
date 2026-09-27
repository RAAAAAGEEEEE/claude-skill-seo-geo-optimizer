# Crawlers de recherche et d'IA : rôles, robots.txt, vérification

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
Version machine de ce tableau : [`../scripts/ai_bots.py`](../scripts/ai_bots.py)
— mettre à jour les deux ensemble.

## La distinction qui compte : quatre rôles

| Rôle | Ce que fait le crawler | Le bloquer, c'est... |
|---|---|---|
| **engine** | Index d'un moteur classique qui alimente aussi ses réponses IA | Disparaître du moteur **et** de ses réponses IA |
| **search** | Index de recherche d'un assistant IA (citations) | Ne plus être cité par cet assistant |
| **user** | Récupération déclenchée par la question d'un utilisateur | Ne plus être lu en direct ; plusieurs ignorent robots.txt |
| **training** | Collecte pour entraîner des modèles | Sortir de l'entraînement, **sans** effet sur la citation |
| **token** | Jeton robots.txt sans user-agent propre | Réglage d'usage, aucune requête ne le porte |

## Tableau par fournisseur

| Fournisseur | engine / search | user | training / token | Source (date) |
|---|---|---|---|---|
| Google | `Googlebot` (Search, AI Overviews, AI Mode, Discover) | `Google-Agent` (agents hébergés par Google, ignore généralement robots.txt), `Google-GeminiNotebook` | `Google-Extended` (jeton : entraînement Gemini + grounding Gemini Apps/Vertex AI) | [common crawlers](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) (2026-07-14), [user-triggered](https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers) (2026-08-19) |
| Microsoft | `bingbot` (Bing et grounding de Copilot) | — | pas de jeton : `NOCACHE` / `NOARCHIVE` en meta | [Bing, 2023-09-22](https://blogs.bing.com/webmaster/september-2023/Announcing-new-options-for-webmasters-to-control-usage-of-their-content-in-Bing-Chat), [Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/manage-public-web-access) (2026-08-18) |
| OpenAI | `OAI-SearchBot` | `ChatGPT-User` (robots.txt non garanti) | `GPTBot` | [OpenAI bots](https://developers.openai.com/api/docs/bots) (consulté 2026-09-27) |
| Anthropic | `Claude-SearchBot` | `Claude-User` (respecte robots.txt) | `ClaudeBot` | [Anthropic](https://support.claude.com/en/articles/8896518) (2026-04-07) |
| Perplexity | `PerplexityBot` | `Perplexity-User` (ignore généralement robots.txt) | — | [Perplexity](https://docs.perplexity.ai/guides/bots) (consulté 2026-09-27) |
| Mistral (Le Chat, renommé Vibe le 2026-08-12) | `MistralAI-Index` | `MistralAI-User` | `MistralAI-Training` | [Mistral](https://docs.mistral.ai/robots) (consulté 2026-09-27) |
| Apple | `Applebot` (Siri, Spotlight, Safari ; suit les règles Googlebot s'il n'est pas nommé) | — | `Applebot-Extended` (jeton, ne crawle pas) | [Apple](https://support.apple.com/en-us/119829) (2026-09-04) |
| Meta | `meta-webindexer` (recherche Meta AI) | `meta-externalfetcher` (peut ignorer robots.txt) | `meta-externalagent` (entraînement et indexation) | [Meta](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/) (consulté 2026-09-27) |
| Amazon | `Amzn-SearchBot` | `Amzn-User` | `Amazonbot` (ignore `Crawl-delay`) | [Amazon](https://developer.amazon.com/amazonbot) (consulté 2026-09-27) |
| DuckDuckGo | `DuckAssistBot` (réponses IA, pas d'entraînement ; effet sous 72 h) | — | — | [DuckDuckGo](https://duckduckgo.com/duckduckgo-help-pages/results/duckassistbot) |
| Common Crawl | — | — | `CCBot` (corpus ouvert) | [Common Crawl](https://commoncrawl.org/ccbot) |
| Brave | pas de user-agent propre : ne crawle que ce que `Googlebot` peut crawler ; désindexer = `noindex` | — | — | [Brave](https://search.brave.com/help/brave-search-crawler) |

Tout ce tableau est **ESTABLISHED** (documentation de chaque fournisseur sur
son propre crawler). Pas de crawler documenté trouvé pour xAI (Grok),
DeepSeek, ByteDance, You.com, Cohere au 2026-09-27.

Les Google IP ranges ont changé d'adresse : `/static/crawling/ipranges/*.json`
([Google, 2026-03-31](https://developers.google.com/search/blog/2026/03/crawler-ip-ranges)).
Anthropic publie les siens depuis août 2026 : `https://claude.com/crawling/bots.json`.

## Ce que robots.txt contrôle réellement

- **Google** : AI Overviews et AI Mode sont contrôlés par `Googlebot` et les
  directives d'aperçu (`nosnippet`, `data-nosnippet`, `max-snippet`,
  `noindex`), **pas** par `Google-Extended`. Depuis le 2026-08-31, un réglage
  Search Console permet aussi d'exclure le site des fonctions IA — voir
  [google-ai-features.md](google-ai-features.md). ESTABLISHED.
- **OpenAI** : bloquer `GPTBot` ne retire pas le site de ChatGPT search ;
  seul `OAI-SearchBot` le fait (un site exclu peut encore apparaître comme
  lien de navigation). Si les deux sont autorisés, OpenAI peut réutiliser un
  même crawl pour les deux usages. ESTABLISHED.
- **Fetchers « user »** : ChatGPT-User, Perplexity-User, Google-Agent,
  meta-externalfetcher et Amzn-User ont des exceptions documentées à
  robots.txt. robots.txt n'est pas un contrôle d'accès ; seul le serveur ou le
  CDN en est un. ESTABLISHED.
- **RFC 9309** : groupes, plus long motif, `allow` gagne les égalités,
  `*` et `$`. Google ne lit que `user-agent`, `allow`, `disallow`,
  `sitemap` (pas `crawl-delay`), traite tout 4xx sauf 429 comme « aucune
  restriction » et un 5xx/429 comme « tout interdit » pendant 12 h puis
  dernière copie valide ([spec Google, 2026-08-31](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)).
  Implémenté dans [`../scripts/robotstxt.py`](../scripts/robotstxt.py).

## robots.txt ne dit pas si le site est accessible

Le CDN peut renvoyer `403` à un crawler que robots.txt autorise — cas réel et
diagnostic dans [cloudflare-ai-access.md](cloudflare-ai-access.md). Toujours
lancer [`../scripts/check_ai_access.py`](../scripts/check_ai_access.py)
avant de conclure. Limite : le test part de votre machine avec un user-agent
simulé ; un CDN qui vérifie les IP peut traiter le vrai bot autrement.

## Exemple de robots.txt « citation autorisée, entraînement refusé »

Décision produit, à présenter et non à trancher. Généré par
`python scripts/generate_sitemap.py pages.json --domain https://exemple.fr --write-robots --ai-policy search-only`.

```
User-agent: *
Allow: /

# Politique 'search-only' : pas d'entrainement, citation autorisee.
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: MistralAI-Training
User-agent: meta-externalagent
User-agent: Amazonbot
User-agent: CCBot
Disallow: /

User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Agent
User-agent: Applebot
User-agent: MistralAI-Index
User-agent: MistralAI-User
User-agent: meta-webindexer
User-agent: meta-externalfetcher
User-agent: Amzn-SearchBot
User-agent: Amzn-User
User-agent: DuckAssistBot
Allow: /

Sitemap: https://exemple.fr/sitemap.xml
```

Sortie réelle du script (exécuté le 2026-09-27). `Googlebot` et `bingbot`
restent couverts par le groupe `*`. Rappel : `Google-Extended: Disallow`
n'enlève pas le site des AI Overviews ; seul le réglage Search Console ou
`nosnippet` le fait.

## Soumission Brave Search (visibilité Claude)

- Brave a été ajouté à la liste des sous-traitants « web search »
  d'Anthropic le 2025-03-19 (constaté par la presse, Anthropic n'a pas
  confirmé publiquement) — **CLAIMED**
  ([TechCrunch, 2025-03-21](https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/)).
  TurboPuffer ajouté le 2026-05-06, selon un tiers — **CLAIMED**.
- Recouvrement : 13 résultats sur 15 au test de lancement (Profound,
  2025-03-21, échantillon minuscule) ; 79,2 % des citations de Claude dans le
  top 10 Brave sur ~35 000 URLs et 400 requêtes (Profound, 2026-07-22) —
  **CLAIMED** (méthode publiée ; Profound vend des outils AEO).
- `https://search.brave.com/submit-url` déclenche un re-crawl, sans garantie
  d'indexation. Manuel et ponctuel, ne pas automatiser.
