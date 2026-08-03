# Agent Readiness (isitagentready.com) — à situer, pas à survendre

Outil Cloudflare (`https://blog.cloudflare.com/agent-readiness/`,
scanner sur `isitagentready.com`) qui mesure « à quel point un site est prêt
à interagir avec des agents IA » — distinct du GEO (être cité dans une
réponse) : il s'agit de savoir si un **agent autonome** peut découvrir,
lire et potentiellement transiger avec le site par lui-même.

## Ce qu'il vérifie (4 catégories notées + 1 informative)
1. **Discoverability** : `robots.txt`, `sitemap.xml`, Link Headers.
2. **Content** : « Markdown for Agents » (le site sert-il une version
   Markdown propre du contenu, en plus du HTML ?).
3. **Bot Access Control** : Content Signals, règles bots IA, Web Bot Auth.
   **Chevauche directement** [cloudflare-ai-access.md](cloudflare-ai-access.md)
   et [`../scripts/check_ai_access.py`](../scripts/check_ai_access.py) — ce
   volet-là est déjà couvert par ce skill.
4. **Capabilities** : Agent Skills, API Catalog, découverte OAuth, MCP
   Server Cards, WebMCP.
5. **Commerce** (informatif, ne compte pas dans le score) : x402, Universal
   Commerce Protocol (UCP), Agentic Commerce Protocol (ACP).

## Réalité de l'adoption (juillet 2026) — pourquoi ce n'est pas un pilier
Cloudflare a analysé 200 000 domaines pour le lancement de l'outil :
- `robots.txt` présent sur 78% des sites, mais configuré pour les moteurs de
  recherche classiques, pas pour les agents.
- **Content Signals : 4% des sites** l'ont déclaré.
- **Markdown for Agents : 3,9%** des sites le servent.
- **MCP Server Cards + API Catalogs réunis : moins de 15 sites** sur les
  200 000 analysés.

Conclusion honnête : c'est un terrain quasi vierge, pas encore une pratique
SEO/GEO établie. Utile à connaître et à re-scorer occasionnellement (surtout
pour un SaaS qui pourrait vouloir être intégré à des workflows d'agents plus
tard), mais **ne pas le prioriser devant les leviers GEO/SEO établis** de ce
skill (accès crawlers, schema, E-E-A-T, Core Web Vitals) — ceux-là ont un
ROI mesurable aujourd'hui, celui-ci est un pari sur l'avenir.

## API
Le scanner s'appuie sur l'API URL Scanner de Cloudflare : passer l'option
`agentReadiness` dans une requête de scan. Nécessite un token Cloudflare
avec la permission URL Scanner (distincte de celle utilisée pour
`check_ai_access.py`, qui ne dépend d'aucun token). Pas d'intégration
scriptée dans ce skill pour l'instant, vu l'adoption réelle mesurée — à
reconsidérer si les chiffres bougent significativement.

## Vérification manuelle
`https://isitagentready.com` — coller l'URL du site, gratuit, aucune
inscription requise au moment de la rédaction.

## Sources
- [Introducing the Agent Readiness score (Cloudflare Blog)](https://blog.cloudflare.com/agent-readiness/)
- [isitagentready.com](https://isitagentready.com/)
