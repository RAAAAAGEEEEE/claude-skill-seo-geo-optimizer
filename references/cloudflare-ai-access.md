# Blocage CDN des crawlers IA (Cloudflare et autres)

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

`robots.txt` déclare une intention ; le CDN décide de la réalité. Un site peut
autoriser tous les crawlers IA dans son `robots.txt` et leur renvoyer `403`
parce qu'une règle Cloudflare/WAF les bloque avant même le serveur d'origine.
Aucun audit HTML ni lecture de `robots.txt` ne le voit : il faut requêter la
page avec le user-agent de chaque crawler et comparer à un navigateur.
→ [`../scripts/check_ai_access.py`](../scripts/check_ai_access.py).

## Cas réel observé (2026-07-23)

Site en production, `robots.txt` avec un bloc `User-agent: ClaudeBot / Allow: /`
ajouté volontairement quelques jours plus tôt :

| Crawler | robots.txt | Réponse |
|---|---|---|
| Googlebot, Bingbot, GPTBot, OAI-SearchBot | allow | 200 |
| ClaudeBot, Claude-SearchBot, Claude-User | allow | **403** |
| PerplexityBot, Perplexity-User, ChatGPT-User | allow | **403** |

Réponse : `Server: cloudflare`, corps `Your request was blocked.` Le site
était incitable par Claude et Perplexity à cause d'une règle CDN que personne
n'avait vue. (Constat de terrain du skill, mesuré ; pas une source publique.)

## Ce que Cloudflare a changé (chronologie, ESTABLISHED sauf mention)

| Date | Changement | Source |
|---|---|---|
| 2025-07-01 | Blocage des crawlers IA par défaut proposé à l'inscription de tout nouveau domaine ; lancement de Pay per crawl (HTTP 402, bêta privée) | [communiqué](https://www.cloudflare.com/press/press-releases/2025/cloudflare-just-changed-how-ai-crawlers-scrape-the-internet-at-large/), [blog](https://blog.cloudflare.com/introducing-pay-per-crawl/) |
| 2025-09-24 | Content Signals Policy : ligne `Content-Signal: search=yes, ai-train=no` dans robots.txt, appliquée aux 3,8 M de domaines en robots.txt géré | [blog](https://blog.cloudflare.com/content-signals-policy/) |
| 2026-02-12 | Markdown for Agents (`Accept: text/markdown`, plans payants) | [changelog](https://developers.cloudflare.com/changelog/post/2026-02-12-markdown-for-agents/) |
| 2026-07-01 | Trafic IA classé en **Search / Agent / Training**, contrôlable par catégorie, y compris en Free ; « Pay Per Crawl évolue vers Pay Per Use » (la doc parle toujours de Pay per crawl, bêta fermée) ; les agents signés (Web Bot Auth) deviennent des bots vérifiés | [blog](https://blog.cloudflare.com/content-independence-day-ai-options/), [communiqué](https://www.cloudflare.com/press/press-releases/2026/cloudflare-allows-the-agentic-internet-to-flourish-with-a-simple-philosophy-your-content-your-rules/) |
| **2026-09-15** | Sur les **pages avec publicité** : Search autorisé, Training et Agent **bloqués par défaut** — nouveaux clients, nouveaux sites, et clients Free existants qui n'ont pas modifié leurs réglages. Les crawlers « mixtes » qui ne séparent pas recherche et entraînement sont bloqués sur ces pages pour qui bloque Training | mêmes sources (annonce du 2026-07-01) |
| 2026-08-21 | Bot Preference Sync : les réglages IA sont réécrits dans robots.txt, actif par défaut pour les nouveaux clients | [blog](https://blog.cloudflare.com/bot-preference-sync/) |
| 2026-09-15 | Statut « Accountable » pour les crawlers mixtes ; engagements attribués à Google, Apple, Microsoft (**CLAIMED** : rapportés par Cloudflare, pas par ces fournisseurs) | [blog](https://blog.cloudflare.com/accountable-mixed-use-ai-crawlers/) |

Non vérifié au 2026-09-27 : un changelog Cloudflare confirmant le
déploiement effectif du 15 septembre. L'annonce est établie, son exécution
doit être constatée site par site avec le script.

Conséquences pratiques :
- Un site Cloudflare Free avec publicité peut avoir basculé **sans action**
  de son propriétaire le 15 septembre 2026. Revérifier tout site audité
  avant cette date.
- La catégorie **Agent** couvre les fetchers déclenchés par l'utilisateur
  (ChatGPT-User, Claude-User, Perplexity-User...) : la bloquer coupe la
  lecture en direct au moment de la question, même si la catégorie Search
  reste ouverte.

## Pourquoi ça arrive encore
1. Réglages par défaut ci-dessus.
2. Fonctions activées en un clic : « Block AI Scrapers and Crawlers », Bot
   Fight Mode, Super Bot Fight Mode, règle WAF héritée.
3. Confusion entraînement/recherche : un blocage global posé en 2023-2024
   contre l'entraînement coupe aussi les crawlers de citation.

## Diagnostic

```bash
python scripts/check_ai_access.py https://example.com/une-page-importante
```

Verdicts : `ok`, `blocked-by-robots` (intention déclarée),
`blocked-upstream` (robots autorise, le CDN refuse : **à traiter en
premier**), `robots-deny-served`, `token-only`, `inconclusive`. Sortie 2 si
la page ne répond pas 200 à un navigateur : ne rien conclure.

Limite : requête depuis votre machine avec un user-agent simulé. Cloudflare
identifie les vrais bots par IP, signature Web Bot Auth ou DNS inverse. Un
`403` ici prouve une règle par user-agent ; un `200` ne garantit pas que le
vrai bot passe. Confirmer dans **AI Crawl Control** (tableau de bord
Cloudflare) ou les journaux d'origine.

## Correction côté Cloudflare (par le propriétaire, jamais sans validation)
1. **AI Crawl Control** : état par crawler et par catégorie Search / Agent /
   Training.
2. **Security > Bots** : « Block AI Scrapers and Crawlers », Bot Fight Mode.
3. **Security > WAF > Custom rules** : règles sur `cf.client.bot`,
   `cf.verified_bot_category` ou des listes d'user-agents.
4. **robots.txt géré / Bot Preference Sync** : vérifier ce que Cloudflare
   écrit dans le robots.txt servi.
5. Revalider avec le script, ne pas se fier au panneau seul.

## La décision de fond (à poser, pas à trancher)
- **Autoriser Search et Agent** = condition nécessaire pour être cité et lu
  en direct par les assistants.
- **Bloquer Training, autoriser Search/Agent** : position intermédiaire
  cohérente (le contenu reste citable sans nourrir les modèles).
- **Pay per crawl / Pay Per Use** : pertinent pour un éditeur qui veut
  monétiser, hors sujet pour un site qui cherche la visibilité.

Autres CDN : Fastly et Akamai proposent des contrôles par crawler et des
partenariats de monétisation (TollBit, 2025) ; aucun blocage par défaut
annoncé à la date de revue.
