# Crawlers IA : robots.txt et llms.txt

## robots.txt vs llms.txt — ne pas confondre
- `robots.txt` = seul mécanisme d'**accès**. C'est lui qui autorise ou bloque
  un crawler.
- `llms.txt` = fichier de **découverte** (description du site + pages clés)
  pour aider un moteur génératif à comprendre le site. **Ce n'est pas un
  mécanisme de contrôle d'accès** — les fournisseurs de crawlers IA ne s'y
  fient pas pour décider quoi indexer. Ne jamais le présenter comme un moyen
  de bloquer ou d'autoriser un bot.

## Deux familles de bots par fournisseur
La plupart des fournisseurs IA font tourner deux bots distincts : un bot
d'**entraînement** (alimente le modèle) et un bot de **recherche/citation**
(utilisé au moment de la requête, pour du RAG en temps réel). Bloquer le bot
de recherche fait perdre les citations ; bloquer le bot d'entraînement
n'empêche pas les citations si le bot de recherche reste autorisé.

| Fournisseur | Bot d'entraînement | Bot de recherche/citation |
|---|---|---|
| OpenAI | `GPTBot` | `OAI-SearchBot`, `ChatGPT-User` |
| Anthropic | `ClaudeBot` | `Claude-SearchBot`, `Claude-User` |
| Perplexity | — | `PerplexityBot`, `Perplexity-User` |
| Google | `Google-Extended` | (déjà couvert par Googlebot standard) |
| Apple | `Applebot-Extended` | — |

## Exemple de configuration robots.txt (autoriser les bots de citation)
```
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: {{url_sitemap}}
```
Ce blocage/déblocage est une décision produit (le site peut avoir une raison
métier de bloquer l'entraînement tout en gardant la citation, ou l'inverse) —
toujours la présenter à l'utilisateur plutôt que de trancher seul, surtout si
le `robots.txt` actuel bloque déjà ces bots intentionnellement.

## Pourquoi ça compte
Une part significative des sites B2B bloque encore au moins un bot IA majeur
par défaut de configuration ("block everything" hérité de 2023-2024), ce qui
exclut le site des réponses génératives sans bénéfice de sécurité réel — ces
bots respectent publiquement `robots.txt`. Vérifier que le blocage, s'il
existe, est un choix explicite et pas un oubli.

## llms.txt — structure minimale
```markdown
# {{Nom du site}}

> {{Description en une phrase de ce que fait le site/produit}}

## Pages clés
- [{{Titre page 1}}]({{url_page_1}}): {{description courte}}
- [{{Titre page 2}}]({{url_page_2}}): {{description courte}}
```

## GEO — soumission Brave Search
Claude (Anthropic) utilise Brave Search comme backend principal pour son
outil de recherche web (Brave est listé comme sous-traitant "web search" par
Anthropic depuis mars 2025 ; des mesures indépendantes observent ~79-87%
de recouvrement entre les résultats cités par Claude et les résultats
organiques non-sponsorisés de Brave, selon l'échantillon et la période).

Conséquence pratique : soumettre une URL sur
`https://search.brave.com/submit-url` peut accélérer son re-crawl par Brave
et donc sa disponibilité pour le web search de Claude.

**Nuances à respecter** (ne jamais présenter autrement) :
- Le formulaire déclenche un re-crawl, **ce n'est ni une garantie
  d'indexation ni de ranking**.
- Ça ne concerne que le web search **au moment de la requête** — pas les
  connaissances natives d'entraînement de Claude (issues du pré-entraînement,
  indépendantes de Brave et non influençables par cette soumission).
- Aucune preuve que *toute* recherche web de Claude passe par Brave à 100% —
  traiter l'overlap observé comme une forte corrélation, pas une certitude
  absolue.
- Soumission manuelle et ponctuelle uniquement (formulaire) — ne pas
  automatiser cette soumission en masse, ça n'apporte rien et peut ressembler
  à du spam de soumission.

## Sources
- [The AI User-Agent Landscape in 2026: A Complete Reference](https://nohacks.co/blog/ai-user-agents-landscape-2026)
- [AI Crawler Access Control: The 2026 Decision Matrix](https://www.digitalapplied.com/blog/ai-crawler-access-control-2026-robots-llms-txt-decision-matrix)
- [Robots.txt & AI Crawlers in 2026: The Full Guide](https://dataimpulse.com/blog/robots-txt-ai-crawlers/)
- [Robots.txt For AI Bots: Control GPTBot, Google-Extended & More](https://capston.ai/robots-txt-for-ai-bots/)
- [Anthropic Lists Two Web-Search Subprocessors for Claude: Brave & TurboPuffer](https://xponent21.com/insights/claude-web-search-brave-turbopuffer/)
- [Does Claude Use Brave Search? What the Brave Submit URL Page...](https://convertos.ai/geo/claude-brave-search-submit-url)
