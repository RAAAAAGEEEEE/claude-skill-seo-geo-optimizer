# Découverte par les agents IA : MCP, API, Agent Readiness

Revu le 2026-09-27 ; WebMCP, A2A, Agent Readiness, Atlas et accessibilité revus le 2026-10-29. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Distinct du GEO (être cité dans une réponse) : il s'agit de savoir si un
**agent** peut découvrir, lire et utiliser un site ou son API par lui-même.
Verdict au 2026-10-29 (inchangé depuis le 2026-09-27) : terrain réel mais marginal. **Ne jamais le
prioriser devant l'accès des crawlers, l'indexation et le contenu.**

## État des surfaces (ESTABLISHED sauf mention)

| Surface | Statut | Réelle source de visibilité aujourd'hui ? | Source |
|---|---|---|---|
| Registre MCP officiel | Préversion depuis 2025-09-08, API v0.1 figée 2025-10-24, pas de GA datée ; alimente des sous-registres | Indirecte seulement | [blog MCP](https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/), [GitHub](https://github.com/modelcontextprotocol/registry) |
| MCP Server Cards (`/.well-known/mcp/server-card.json`, SEP-1649) | Brouillon ; absent de la spec MCP 2026-07-28 (qui ajoute `server/discover`) | Non | [SEP-1649](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649), [changelog spec](https://modelcontextprotocol.io/specification/2026-07-28/changelog) |
| Plugins ChatGPT / Codex (Apps SDK sur MCP) | Annuaire avec revue : identité vérifiée, serveur MCP public, domaine vérifié | **Oui**, pour qui construit une app et passe la revue | [OpenAI](https://developers.openai.com/apps-sdk/deploy/submission) |
| Connecteurs Claude | Annuaire depuis 2025-07-14 (connecteurs distants : plans payants) | Oui, même logique | [Anthropic](https://claude.com/blog/connectors-directory) |
| WebMCP | Brouillon de rapport du Web Machine Learning Community Group (ni standard W3C, ni piste de standardisation), 2026-10-27. Surface JavaScript `document.modelContext` (`registerTool`, `getTools`, `executeTool`). Chrome : essai d'origine depuis Chrome 149 ; API déclarative par attributs de formulaire (`toolname`, `tooldescription`, `toolautosubmit`, `toolparamdescription`). La date du 2026-02-10 est celle du programme d'aperçu, pas de l'essai d'origine. Un alias `navigator.modelContext` dans Chrome 150 est affirmé par des blogs de tiers, non lu dans la doc Chrome : **CLAIMED, à reconfirmer** | Non (expérimental) | [spec](https://webmachinelearning.github.io/webmcp/) (2026-10-27), [Chrome](https://developer.chrome.com/docs/ai/webmcp) (publiée 2026-05-18, maj 2026-10-07), [API déclarative](https://developer.chrome.com/docs/ai/webmcp/declarative-api) (maj 2026-09-25) |
| A2A (Agent2Agent) | Version 1.0.0 « Latest Released » (ESTABLISHED, consulté 2026-10-29). Carte d'agent à `/.well-known/agent-card.json` : chemin lu dans des sources de tiers, pas dans la spécification — **CLAIMED, à reconfirmer** | Non mesurable | [spec](https://a2a-protocol.org/latest/specification/) (consulté 2026-10-29) ; [API Evangelist](https://apievangelist.com/2026/07/29/most-published-agent-cards-are-not-actually-a2a/) (2026-07-29, tiers) |
| API catalog (`/.well-known/api-catalog`, RFC 9727, juin 2025) | Standard proposé | Non mesurable | [RFC 9727](https://www.rfc-editor.org/rfc/rfc9727) |
| NLWeb (Microsoft, 2025-05-19) | Peu d'activité en 2026 | Aucune preuve qu'un assistant l'interroge | [Microsoft](https://news.microsoft.com/source/features/company-news/introducing-nlweb-bringing-conversational-interfaces-directly-to-the-web/) |
| UCP (Google), ACP (Stripe/OpenAI), AP2 | Commerce agentique (UCP alimente le paiement dans AI Mode/Gemini) | Seulement pour un marchand | [ucp.dev](https://ucp.dev/), [agenticcommerce.dev](https://www.agenticcommerce.dev/) |
| Flux produits ChatGPT | Spécification JSONL/CSV, 9 champs requis | Pour un marchand | [OpenAI](https://developers.openai.com/commerce/specs/feed) |

## Agent Readiness (Cloudflare)
Score lancé le 2026-04-17 (`isitagentready.com`) : découvrabilité
(robots.txt, sitemap, en-têtes Link), contenu (Markdown), accès des bots
(Content Signals, Web Bot Auth), capacités (Agent Skills, API catalog,
OAuth, MCP Server Card, WebMCP) ; commerce informatif (x402, UCP, ACP).
Adoption mesurée sur 200 000 domaines : Content Signals 4 %, Markdown 3,9 %,
MCP Server Cards + API catalogs < 15 sites (CLAIMED, méthode publiée :
Cloudflare vend ces fonctions). Vérification manuelle gratuite sur
`https://isitagentready.com`.

Contrôles et chemins que l'outil teste (ESTABLISHED : description de son
propre outil, [blog Cloudflare](https://blog.cloudflare.com/agent-readiness/),
2026-04-17, modifié 2026-07-15) :

| Contrôle | Chemin ou signal |
|---|---|
| Découvrabilité | `robots.txt`, sitemap, en-tête `Link: <...>; rel="api-catalog"` |
| Catalogue d'API | `/.well-known/api-catalog` |
| Compétences d'agent | `/.well-known/agent-skills/index.json` |
| Serveur MCP | `/.well-known/mcp/server-card.json` |
| Identité des bots | `/.well-known/http-message-signatures-directory` (Web Bot Auth) |
| Contenu | `Accept: text/markdown` |
| Préférences d'usage | Content Signals dans robots.txt |

Pour un site de contenu ou un portfolio, ces contrôles ne sont pas un objectif
en soi : le score mesure l'adoption de fonctions, pas la visibilité (aucune
étude trouvée ne relie ces fichiers à des citations).

## Accessibilité comme interface des agents
- Lighthouse a une catégorie « Agentic Browsing » avec quatre familles
  d'audits : WebMCP, `llms.txt`, accessibilité pour agents, stabilité de la
  mise en page. ESTABLISHED (outil de test de Chrome :
  [llms.txt](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt),
  [accessibilité](https://developer.chrome.com/docs/lighthouse/agentic-browsing/accessibility-for-agents),
  maj 2026-05-05).
- L'idée sous-jacente : un agent lit l'arbre d'accessibilité de la page ;
  libellés de formulaire, rôles et noms corrects l'aident. Que cela change
  l'usage réel des agents n'est pas démontré : **CLAIMED**.
- OpenAI recommandait des balises ARIA pour son agent dans Atlas
  ([annonce de lancement](https://openai.com/index/introducing-chatgpt-atlas/),
  2025-10-21, ESTABLISHED comme annonce). Ce produit aurait été arrêté
  (ci-dessous) : la consigne ARIA reste une bonne pratique d'accessibilité,
  pas un levier propre à OpenAI.

## ChatGPT Atlas : arrêt annoncé
Annonce du 2026-07-09 (arrêt visé le 2026-08-09) ; le navigateur et l'agent
seraient déplacés dans l'app de bureau (ChatGPT Work) et dans une extension
Chrome. Source : la presse, qui cite un représentant d'OpenAI sur X
([9to5Mac, 2026-07-09](https://9to5mac.com/2026/07/09/openai-is-discontinuing-chatgpt-atlas-its-standalone-desktop-browser/)).
Aucune page d'OpenAI relue : **CLAIMED, à reconfirmer** avant de s'en servir.

## Recommandations par type de site
- **Site de contenu / référence** : une API documentée (OpenAPI) et, si
  pertinent, un serveur MCP en lecture seule rendent les données
  exploitables par les agents qui les trouvent via la page elle-même
  (lien visible, `WebAPI` en JSON-LD). Publier dans un annuaire (plugins
  ChatGPT, connecteurs Claude, registre MCP) est une **action externe** à
  décider par le propriétaire (compte, vérification de domaine).
- **SaaS** : même logique ; OAuth et catalogue d'API si des agents doivent
  agir pour un utilisateur.
- **Commerce** : flux produits et protocole de paiement (UCP/ACP) selon
  les plateformes visées.
- **Commerce local / vitrine** : rien à faire ici au 2026-09-27.

Pas de script dans ce skill : l'adoption mesurée ne le justifie pas encore.
