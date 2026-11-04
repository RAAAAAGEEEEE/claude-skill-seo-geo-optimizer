# Robots malveillants et faux trafic : contrôles d'audit

Revu le 2026-11-04 (v2.7.0). Base : rapport de recherche du 2026-11-04 sur un serveur nginx
(Ubuntu 24.04, nginx 1.24) qui héberge des sites derrière Cloudflare et des sites sans Cloudflare,
avec mesures sur 639 572 lignes de journal (21/10 au 04/11/2026) et pages officielles relues le
2026-11-04. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Pourquoi un audit SEO/GEO s'en occupe : deux dégâts, pas un seul.
1. Les **scanners** (`.env`, `.git`, `.php`, `wp-*`) coûtent peu de charge mais saturent journaux et
   statistiques. Mesure : 10,6 % des lignes d'un serveur réel (SUPPORTED, mesure locale).
2. Le **faux trafic** fausse tout ce qui sert à décider : adresses Cloudflare prises pour des
   visiteurs, serveur qui se visite lui-même (36 % du journal courant, ESTABLISHED, mesure locale),
   navigateurs sans tête. On ne règle pas ça en bloquant, on règle ça en **filtrant ce qu'on compte**.
   Contexte chiffré : plus de 53 % du trafic web est automatisé, dont 40 % malveillant (rapport Bad
   Bot 2026 de Thales/Imperva, 2026-05-05 ; chiffres de leur parc de clients, CLAIMED pour la
   méthode).
Et un troisième risque, propre au SEO : **bloquer par erreur un bon robot** (aperçu WhatsApp,
Googlebot, moteurs IA voulus). Un faux positif coûte plus cher qu'un scanner toléré.

Mesure automatique : `python scripts/hygiene_check.py probes --site <url>` (sondes publiques) et
`python scripts/hygiene_check.py logs <journal> --internal-ip <ip>` (journal fourni par le propriétaire ;
comptes seulement, aucune adresse écrite). Voir [../docs/USAGE.md](../docs/USAGE.md).

## Contrôles de l'audit

| # | Contrôle | Comment le vérifier | Étiquette, source |
|---|---|---|---|
| B1 | Les chemins de scanners sont coupés en **444** (connexion fermée sans réponse), `/.well-known/` reste ouvert | `hygiene_check.py probes` : verdict `closed` attendu ; un `403`/`404` = P2 (correct mais bruyant) ; un `200` = P1 | ESTABLISHED : « 444 closes a connection without sending a response » ([nginx.org](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)). Le gain sur le journal : SUPPORTED |
| B2 | Les bons robots et les aperçus de lien ne sont ni bloqués ni défiés (WhatsApp, `facebookexternalhit`, Googlebot, bingbot, OAI-SearchBot, ClaudeBot, PerplexityBot) | `probes` : verdict `ok` attendu sur l'accueil pour chaque agent simulé ; `challenge`, 403, 429, 503 = P1 | ESTABLISHED pour le principe (l'agent se falsifie, l'adresse se vérifie : listes JSON officielles de Google, Bing, OpenAI, Anthropic, Perplexity ; table du rapport, relue le 2026-11-04). Limite : agent simulé, un `200` ne prouve pas que le vrai robot passe |
| B3 | Le 444 ne s'applique pas par agent aux robots SEO déclarés sans décision : `robots.txt` d'abord, 444 seulement s'ils l'ignorent | Revue de la configuration (`map` sur l'agent) | SUPPORTED (déduction : un agent se falsifie en une ligne, un `map` sert à classer, pas à prouver) |
| B4 | `real_ip` configuré derrière Cloudflare : `set_real_ip_from` pour chaque plage Cloudflare, puis `real_ip_header CF-Connecting-IP`, liste mise à jour régulièrement (script planifié) | `hygiene_check.py logs` : plus de 1 % de lignes dont le « client » est une plage Cloudflare = P1 `real-ip-missing` | ESTABLISHED, [doc Cloudflare](https://developers.cloudflare.com/support/troubleshooting/restoring-visitor-ips/restoring-original-visitor-ips/) (maj 2026-04-23, relue le 2026-11-04) : « That list of prefixes needs to be updated regularly » |
| B5 | Sans `real_ip`, `limit_req` et fail2ban voient Cloudflare : une limite par adresse est partagée entre tous les visiteurs d'un même point de Cloudflare ; un jail fail2ban bannirait Cloudflare | Revue : toute zone `limit_req` ou jail posé sur un site proxifié suppose B4 | SUPPORTED (déduction directe de B4, à confirmer par un test) |
| B6 | Pour un site derrière Cloudflare, le blocage des scanners se fait **chez Cloudflare** (règle WAF), pas par un bannissement pare-feu sur le serveur : les paquets viennent de Cloudflare, pas du visiteur | Revue de l'architecture ; règles du plan Free : 5 règles personnalisées | ESTABLISHED pour les limites du plan Free ([doc custom rules](https://developers.cloudflare.com/waf/custom-rules/)) ; le raisonnement d'architecture : SUPPORTED |
| B7 | Les statistiques excluent le **trafic interne** (serveur lui-même, surveillances, VPN du propriétaire) | `logs --internal-ip <ip>` : plus de 5 % de lignes internes = P1 `internal-traffic` ; exclusion par second `access_log` conditionnel ou par l'outil de comptage | ESTABLISHED, mesure locale (36 % sur le journal courant du serveur audité). Aucune adresse interne fournie = contrôle « non mesuré », jamais « OK » |
| B8 | Les statistiques excluent les **robots** : comptage par script JavaScript (un robot sans JavaScript n'est pas compté), journaux gardés en contrôle croisé, navigateurs sans tête comptés à part | `logs` : part `headless` ; revue de l'outil de comptage | Voir la table des outils ci-dessous |
| B9 | Un agent qui se dit bon robot mais dont l'adresse est hors des listes officielles est classé « faux robot » et exclu | `python scripts/crawler_logs.py <journal> --site <url>` (déjà dans le skill) | ESTABLISHED (méthode : listes JSON des fournisseurs) |
| B10 | **Bot Fight Mode** : non activé sans inventaire des appels automatiques de la zone (webhooks de paiement, API, formulaires, application mobile) | Tableau de bord Cloudflare (réglage de compte, non lisible par script) ; liste des appelants automatiques | ESTABLISHED, [doc Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/) (maj 2026-08-03) : il « may challenge API or mobile app traffic » et ne tourne pas sur le Ruleset Engine, donc **Skip, Bypass et Allow n'ont aucun effet** ; l'exception passe par Super Bot Fight Mode (offre payante) |
| B11 | **« Block AI bots »** (ancien réglage) et la politique « AI Crawler and Agent access policies » ne bloquent pas les moteurs IA voulus (GPTBot/OAI-SearchBot, ClaudeBot, PerplexityBot) | `python scripts/check_ai_access.py <url>` (`blocked-upstream` = P0) puis tableau de bord : Security > Settings > AI Crawler and Agent access policies | ESTABLISHED : politique par comportement Search / Agent / Training, tout sur Allow pour un nouveau domaine ([doc](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/), maj 2026-11-02). Qu'un ancien réglage « Block AI bots » persiste sur une zone existante : CLAIMED, à constater site par site |
| B12 | Le serveur d'origine joignable directement par son adresse contourne les règles du CDN | Revue ; restreindre l'origine aux plages du CDN touche au réseau | ESTABLISHED (architecture) ; **décision du propriétaire**, jamais appliquée seule |
| B13 | Aucun tarpit, labyrinthe ni lien caché ajouté pour « piéger » les robots sur un site qui veut être indexé | Revue | SUPPORTED : tarpits (Nepenthes, Iocaine) coûtent autant que servir le site et peuvent piéger des moteurs légitimes ; un lien caché peut être lu comme dissimulation. Revendication « 94 % du trafic de robots éliminé » : CLAIMED, créateur d'Iocaine |
| B14 | Pas de défi par preuve de travail (Anubis) devant un site vitrine dont l'enjeu est d'être lu par Google et par les moteurs IA | Revue | SUPPORTED (avis du rapport) ; fait établi : le comportement par défaut défie ce qui ressemble à un navigateur et les aperçus de lien tant que `openGraph` n'est pas activé (docs Anubis, lues le 2026-11-04) |

## Statistiques : ce que chaque outil filtre vraiment (relu le 2026-11-04)

| Outil | Ce qu'il filtre | Limite déclarée | Étiquette |
|---|---|---|---|
| GoatCounter 2.7.0 (2025-12-15) | robots qui s'annoncent comme robots | « il est facile pour un script malveillant de se faire passer pour Firefox ou Chrome » ([FAQ](https://www.goatcounter.com/help/faq)) | ESTABLISHED |
| Plausible (doc du 2026-10-09) | agents connus, spam de référents, environ 40 800 plages de centres de données, schémas non humains | « aucun filtre n'est parfait », visiteurs en VPN ou iCloud Private Relay filtrés à tort ; 30 adresses d'exclusion par site au plus ([doc](https://plausible.io/docs/bot-traffic-filtering)) | ESTABLISHED |
| Umami 3.4.1 | `isbot` sur l'agent ; `DISABLE_BOT_CHECK` le coupe | un navigateur sans tête qui ne se déclare pas passe (code source lu le 2026-11-04) | ESTABLISHED |
| GoAccess (journaux) | `--ignore-crawlers`, `--unknowns-as-crawlers`, `--exclude-ip`, `--browsers-file` ([man](https://goaccess.io/man)) | compte aussi tout ce qui ne lance pas de JavaScript | ESTABLISHED |

Ordre de gain pour des statistiques fiables : 1. corriger la source (B4 puis B7), 2. compter par script
JavaScript, 3. classer par vérification d'adresse (B9), 4. juger l'audience sur l'engagement (durée,
défilement, objectifs) plutôt que sur le nombre de visites (SUPPORTED), 5. surveiller l'écart entre
pages demandées dans le journal et visites comptées : un écart qui grandit signale de nouveaux
robots (SUPPORTED, raisonnement).

## Ce que le skill ne fait pas
- Il ne modifie ni nginx, ni fail2ban, ni Cloudflare : il liste, le propriétaire (ou l'agent
  d'infrastructure, sur accord) applique. Tout nouveau réglage nginx de limite se teste d'abord en
  `limit_req_dry_run on` (nginx 1.17.1 ou plus, ESTABLISHED, [nginx.org](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)).
- Il ne lit que des GET publics du site audité, et un journal que le propriétaire fournit. Les
  adresses du journal sont des données personnelles : comptes seulement.
- Un robot « non vérifiable » (Meta, Amazon, WhatsApp : aucune liste d'adresses officielle) n'est
  jamais déclaré « vérifié ».
