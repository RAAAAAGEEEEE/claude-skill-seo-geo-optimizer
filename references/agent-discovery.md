# Découverte par les agents IA : MCP, API, Agent Readiness

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Distinct du GEO (être cité dans une réponse) : il s'agit de savoir si un
**agent** peut découvrir, lire et utiliser un site ou son API par lui-même.
Verdict au 2026-09-27 : terrain réel mais marginal. **Ne jamais le
prioriser devant l'accès des crawlers, l'indexation et le contenu.**

## État des surfaces (ESTABLISHED sauf mention)

| Surface | Statut | Réelle source de visibilité aujourd'hui ? | Source |
|---|---|---|---|
| Registre MCP officiel | Préversion depuis 2025-09-08, API v0.1 figée 2025-10-24, pas de GA datée ; alimente des sous-registres | Indirecte seulement | [blog MCP](https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/), [GitHub](https://github.com/modelcontextprotocol/registry) |
| MCP Server Cards (`/.well-known/mcp/server-card.json`, SEP-1649) | Brouillon ; absent de la spec MCP 2026-07-28 (qui ajoute `server/discover`) | Non | [SEP-1649](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649), [changelog spec](https://modelcontextprotocol.io/specification/2026-07-28/changelog) |
| Plugins ChatGPT / Codex (Apps SDK sur MCP) | Annuaire avec revue : identité vérifiée, serveur MCP public, domaine vérifié | **Oui**, pour qui construit une app et passe la revue | [OpenAI](https://developers.openai.com/apps-sdk/deploy/submission) |
| Connecteurs Claude | Annuaire depuis 2025-07-14 (connecteurs distants : plans payants) | Oui, même logique | [Anthropic](https://claude.com/blog/connectors-directory) |
| WebMCP | Brouillon W3C (Web Machine Learning CG), essai Chrome depuis 2026-02-10 | Non (expérimental) | [Chrome](https://developer.chrome.com/blog/webmcp-epp) |
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
