# Crawlers IA : robots.txt, llms.txt, Brave

## Les deux familles de bots (la distinction qui compte)
La plupart des fournisseurs font tourner **deux** bots. Les confondre est
l'erreur la plus coûteuse en GEO.

| Fournisseur | Entraînement (nourrit le modèle) | Recherche/citation (au moment de la requête) |
|---|---|---|
| OpenAI | `GPTBot` | `OAI-SearchBot`, `ChatGPT-User` |
| Anthropic | `ClaudeBot` | `Claude-SearchBot`, `Claude-User` |
| Perplexity | — | `PerplexityBot`, `Perplexity-User` |
| Google | `Google-Extended` | (Googlebot standard) |
| Apple | `Applebot-Extended` | — |

Bloquer un bot d'**entraînement** n'empêche pas d'être cité. Bloquer un bot
de **recherche** rend la citation impossible, quel que soit le contenu.

## robots.txt ne suffit pas à savoir si le site est accessible
`robots.txt` est déclaratif. Le CDN peut renvoyer `403` à un bot que le
`robots.txt` autorise — cas réel documenté et outillé dans
[cloudflare-ai-access.md](cloudflare-ai-access.md). **Toujours vérifier
l'accès réel** avec [`../scripts/check_ai_access.py`](../scripts/check_ai_access.py)
avant de conclure quoi que ce soit sur la visibilité GEO d'un site.

## Exemple de robots.txt (autoriser la citation)
```
User-agent: *
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: {{url_sitemap}}
```
Autoriser ou bloquer est une **décision produit** (contenu ouvert vs
monétisation, cf. Pay Per Use de Cloudflare) : la présenter, ne pas la
trancher seul. Si un blocage existe déjà, vérifier qu'il est intentionnel et
pas hérité d'une configuration de 2023-2024.

## llms.txt — statut réel, à ne pas survendre
Créer un `llms.txt` ne nuit pas, mais les faits en juillet 2026 :

- **Google ne l'utilise pas.** Le guide officiel « AI features » (mis à jour
  15 juin 2026) dit explicitement : *« You don't need to create new machine
  readable files, AI text files, or markup to appear in these features »*.
  John Mueller l'a comparé à la balise `meta keywords` — déclaratif, donc
  manipulable, donc ignoré.
- **Il n'est quasiment jamais lu.** Étude Ahrefs sur 137 000 sites : **97%
  des fichiers `llms.txt` n'ont reçu aucune requête** en mai 2026. Les
  crawlers IA récupèrent le HTML directement.
- **Adoption ~10%** des domaines (étude SE Ranking, 300 000 domaines).
- **Ce n'est pas un contrôle d'accès.** Seul `robots.txt` en est un. Ne
  jamais le présenter comme un moyen de bloquer ou d'autoriser un bot.

Usage résiduel légitime : documentation technique destinée aux outils de
codage IA. Pour un site vitrine, SaaS ou commerce local, le classer en P2 au
mieux — et ne jamais en faire une recommandation prioritaire dans un audit.

Structure minimale si créé quand même :
```markdown
# {{Nom du site}}

> {{Description en une phrase}}

## Pages clés
- [{{Titre}}]({{url}}): {{description courte}}
```

## GEO — soumission Brave Search
Claude utilise Brave Search comme backend principal de son outil de
recherche web (Brave listé comme sous-traitant « web search » par Anthropic
depuis mars 2025 ; recouvrement observé de ~79-87% entre les résultats cités
par Claude et l'organique Brave, selon l'échantillon).

Soumettre une URL sur `https://search.brave.com/submit-url` peut accélérer
son re-crawl côté Brave.

Nuances à conserver :
- Déclenche un re-crawl, **ni garantie d'indexation ni de ranking**.
- Ne concerne que la recherche web au moment de la requête — pas les
  connaissances d'entraînement du modèle.
- L'overlap est une forte corrélation, pas une certitude que 100% des
  recherches de Claude passent par Brave.
- Soumission manuelle et ponctuelle ; ne pas automatiser en masse.

## Sources
- [Google — AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) (position officielle sur les fichiers IA)
- [Ahrefs — We Analyzed 137K Sites: 97% of llms.txt Files Never Get Read](https://ahrefs.com/blog/llmstxt-study/)
- [Google Confirms LLMs.txt Has No Current Implementation (SEJ)](https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/)
- [The AI User-Agent Landscape in 2026](https://nohacks.co/blog/ai-user-agents-landscape-2026)
- [Anthropic Lists Two Web-Search Subprocessors: Brave & TurboPuffer](https://xponent21.com/insights/claude-web-search-brave-turbopuffer/)
