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

## Sources
- [The AI User-Agent Landscape in 2026: A Complete Reference](https://nohacks.co/blog/ai-user-agents-landscape-2026)
- [AI Crawler Access Control: The 2026 Decision Matrix](https://www.digitalapplied.com/blog/ai-crawler-access-control-2026-robots-llms-txt-decision-matrix)
- [Robots.txt & AI Crawlers in 2026: The Full Guide](https://dataimpulse.com/blog/robots-txt-ai-crawlers/)
- [Robots.txt For AI Bots: Control GPTBot, Google-Extended & More](https://capston.ai/robots-txt-for-ai-bots/)
