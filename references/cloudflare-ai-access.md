# Blocage CDN des crawlers IA (Cloudflare et autres)

Le point aveugle le plus courant en GEO en 2026 : **`robots.txt` déclare une
intention, le CDN décide de la réalité.** Un site peut autoriser
explicitement tous les bots IA dans son `robots.txt` et malgré tout leur
renvoyer `403` parce qu'une règle Cloudflare/WAF les bloque en amont, avant
même que le serveur d'origine ne soit consulté.

Aucun audit HTML, aucun `curl` classique et aucune lecture de `robots.txt`
ne détecte ce cas. Il faut requêter le site **avec le user-agent de chaque
bot** et comparer.

→ [`scripts/check_ai_access.py`](../scripts/check_ai_access.py) fait
exactement ça, sans authentification.

## Cas réel observé (2026-07-23)

Sur un site en production dont le `robots.txt` contenait un bloc
`User-agent: ClaudeBot / Allow: /` ajouté volontairement quelques jours plus
tôt, avec en commentaire « vise activement les citations par les moteurs
génératifs » :

| Bot | robots.txt | Réponse réelle |
|---|---|---|
| Googlebot | allow | 200 |
| Bingbot | allow | 200 |
| GPTBot | allow | 200 |
| OAI-SearchBot | allow | 200 |
| Google-Extended | allow | 200 |
| **ClaudeBot** | allow | **403** |
| **Claude-SearchBot** | allow | **403** |
| **Claude-User** | allow | **403** |
| **PerplexityBot** | allow | **403** |
| **Perplexity-User** | allow | **403** |
| **ChatGPT-User** | allow | **403** |

Réponse : `Server: cloudflare`, corps `Your request was blocked.`

Conséquence concrète : le site était **structurellement incitable par Claude
et Perplexity** — pas à cause de son contenu, de son schema ou de son
autorité, mais d'une règle CDN que personne n'avait vue. Le travail SEO/GEO
on-site sur ces pages avait un plafond de zéro pour ces moteurs.

## Pourquoi ça arrive

1. **Réglages par défaut Cloudflare.** Cloudflare a annoncé qu'à partir du
   **15 septembre 2026**, les nouveaux sites et les comptes gratuits basculent
   par défaut vers « autoriser la recherche, bloquer l'entraînement et les
   agents » sur les pages avec publicité, et bloquent les crawlers *mixtes*
   (à la fois moteur de recherche et agent IA) qui ne laissent pas le choix au
   site. Un site peut donc changer de comportement sans aucune action de son
   propriétaire.
2. **Fonctionnalités activées en un clic** : « Block AI Scrapers and
   Crawlers », Bot Fight Mode, Super Bot Fight Mode, ou une règle WAF héritée
   d'une configuration de sécurité passée.
3. **Confusion entraînement/recherche.** Beaucoup de propriétaires ont
   activé un blocage global en 2023-2024 pour empêcher l'entraînement, sans
   réaliser que cela coupe aussi les bots de *citation* (ceux qui vont
   chercher la page au moment où un utilisateur pose une question). Bloquer
   `GPTBot` n'empêche pas d'être cité ; bloquer `OAI-SearchBot` si.

## Diagnostic

```bash
python scripts/check_ai_access.py https://example.com
```

Le script distingue trois états, et c'est la distinction qui compte :
- `robots=allow, HTTP 200` → réellement accessible.
- `robots=allow, HTTP 403` → **blocage CDN silencieux**, l'intention du site
  est trahie par l'infrastructure. C'est le cas à traiter en priorité.
- `robots=DENY` → blocage volontaire et cohérent (à confirmer avec le
  propriétaire, mais au moins déclaratif et intentionnel).

## Correction côté Cloudflare

Ce sont des réglages de compte, à faire par le propriétaire du site — ne
jamais les modifier sans validation explicite, c'est une décision produit
(cf. le compromis contenu-gratuit vs monétisation ci-dessous).

1. **Security > Bots** : vérifier « Block AI Scrapers and Crawlers » (le
   désactiver si l'objectif est la visibilité GEO).
2. **Security > WAF > Custom rules** : chercher toute règle filtrant sur
   `cf.client.bot`, `http.user_agent contains "Bot"`, ou une liste d'UA IA.
3. **Security > Settings** : Bot Fight Mode / Super Bot Fight Mode peuvent
   bloquer des bots vérifiés selon le plan.
4. Après modification, **revalider avec le script** — ne pas se fier au
   panneau de configuration seul.

## La décision de fond (à poser à l'utilisateur, pas à trancher)

Bloquer ou autoriser les crawlers IA est un **arbitrage produit**, pas une
bonne pratique universelle :

- **Autoriser** = condition nécessaire pour être cité dans ChatGPT, Claude,
  Perplexity, AI Overviews. Sans accès, aucune optimisation de contenu ne
  peut compenser.
- **Bloquer l'entraînement** (`GPTBot`, `ClaudeBot`, `Google-Extended`,
  `Applebot-Extended`) tout en **autorisant la recherche**
  (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`, `*-User`) est une
  position intermédiaire cohérente : le contenu reste citable sans nourrir
  les modèles.
- Cloudflare pousse par ailleurs un modèle de rémunération (« Pay Per
  Crawl », devenu « Pay Per Use ») où le site est payé quand son contenu
  apparaît dans une réponse IA. Pertinent pour un éditeur de contenu, hors
  sujet pour un site vitrine ou SaaS qui cherche de la visibilité.

Présenter ces options et laisser choisir. Pour un site dont l'objectif est
l'acquisition (SaaS, vitrine, commerce local), autoriser au moins les bots de
recherche est presque toujours le bon choix — mais ça reste au propriétaire
de le décider.

## Sources
- [Cloudflare Will Block AI Crawlers Unless Sites Opt In](https://dataconomy.com/2026/07/03/cloudflare-will-block-ai-crawlers-unless-sites-opt-in/)
- [Cloudflare's new policy pushes AI companies to pay for publishers' content (TechCrunch)](https://techcrunch.com/2026/07/01/cloudflares-new-policy-pushes-ai-companies-to-pay-for-publishers-content/)
- [Cloudflare gives AI crawlers a September deadline (TNW)](https://thenextweb.com/news/cloudflare-block-ai-crawlers-pay-publishers)
