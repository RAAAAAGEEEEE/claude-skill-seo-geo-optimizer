# Checklist — uniquement ce que les scripts ne peuvent PAS vérifier

Revu le 2026-09-28 (v2.3.0).

Tout ce qui est automatisable en est retiré. Ne pas revérifier à la main ce
que `run_audit.py` contrôle :
- HTTP, redirections, noindex et nosnippet ;
- title, description, canonical, H1, lang, JSON-LD ;
- hreflang et langue ;
- sitemaps et lastmod ;
- 404 des URLs inconnues ;
- maillage : orphelines, profondeur, ancres, cocon par répertoire ;
- robots.txt et accès par crawler ;
- PageSpeed, CrUX, Search Console et clé IndexNow, si un accès est fourni.

## Avant de commencer
- [ ] `python scripts/run_audit.py --site <url>` exécuté — si un P0 sort
      (crawler de recherche/citation bloqué, accueil ou robots.txt
      illisible), le traiter avant tout le reste.
- [ ] Les modules `skipped` du rapport sont assumés (accès non fourni) ou
      corrigés (variable d'environnement, [../docs/CONFIGURATION.md](../docs/CONFIGURATION.md)).

## Réglages qu'aucun script ne voit (accès au compte requis)
- [ ] Search Console > Paramètres > **« Search generative AI »** : sur
      Inclure, sauf décision contraire du propriétaire (Exclure = absent des
      AI Overviews et d'AI Mode).
- [ ] Search Console > rapport **Generative AI performance** : impressions
      dans les fonctions IA (interface seulement).
- [ ] Bing Webmaster Tools > **AI Performance** : citations dans Copilot.
- [ ] Tableau de bord CDN (Cloudflare **AI Crawl Control**, Bot Fight Mode,
      règles WAF) : cohérent avec la décision d'ouverture aux crawlers ;
      bascule du 2026-09-15 sur les pages avec publicité.

## Robots malveillants et faux trafic (voir [bot-traffic-hygiene.md](bot-traffic-hygiene.md))
- [ ] `hygiene_check.py probes` : scanners en `closed`, robots d'aperçu et de recherche en `ok`.
- [ ] Derrière Cloudflare : `real_ip` en place (`hygiene_check.py logs`, `real-ip-missing` absent).
- [ ] Statistiques : trafic interne et robots exclus ; une adresse interne non fournie = non mesuré.
- [ ] Tableau de bord Cloudflare : Bot Fight Mode inactif ou appels automatiques (paiement, API)
      inventoriés ; « Block AI bots » et politique des robots IA cohérents avec l'ouverture voulue.
- [ ] Origine joignable directement : décision du propriétaire.

## Contenu utile, petit site (voir [helpful-content-small-site.md](helpful-content-small-site.md))
- [ ] Chaque page répond à un acheteur précis ; le site a un but principal (H1).
- [ ] Aucun lot de pages de masse ; `hygiene_check.py content` sans `near-duplicate-pages` (H2, H7).
- [ ] Preuve de première main sur chaque page de fond, sans avis ni cas client inventés (H3).
- [ ] Auteur réel visible, page auteur et À-propos réelles (H4, H5).
- [ ] Rythme de publication que la relecture suit ; dates modifiées seulement après un vrai changement (H6).

## Tests manuels de praticiens (ajout du 2026-11-08, CLAIMED, voir [french-practitioners.md](french-practitioners.md))
- [ ] Test « mon texte sur une autre page » (B-N3) : si le texte était collé sur le site d'un autre, quelqu'un
      s'en apercevrait-il ? Sinon, la page n'apporte rien de propre.
- [ ] « Mot mystère » (B-N1) : retirer le mot-clé exact des 200 à 300 premiers mots ; un lecteur compétent
      devine-t-il encore le sujet ?
- [ ] Prix, plans et faits critiques lisibles dans le HTML brut (`curl`), pas seulement après JavaScript.
- [ ] Collision de noms : la marque a-t-elle un homonyme (autre domaine, autre extension) que les moteurs
      confondent ? Le vérifier par une recherche de la marque seule.
- [ ] Suivi GEO manuel : 3 à 5 requêtes fixes, relevées chaque semaine en session privée déconnectée (un compte
      connecté flatte les résultats), dans un journal daté.
- [ ] Après toute modification faite par une IA : relire le diff (retraits silencieux de tableaux ou de
      sections) et contrôler le site réel (V15).

## Jugement éditorial
- [ ] Le title donne-t-il envie de cliquer, pas seulement « présent » ?
- [ ] La meta description donne-t-elle une raison de cliquer ?
- [ ] Chaque section commence-t-elle par une réponse directe ?
- [ ] Le texte porte-t-il des preuves vérifiables (chiffres sourcés,
      citations, dates) plutôt que des généralités ?
- [ ] Le contenu apporte-t-il quelque chose d'original (donnée propriétaire,
      expérience réelle, chiffre daté) ?
- [ ] Contenu important rendu dans le HTML initial, pas seulement en
      JavaScript ni caché dans des onglets ou des PDF ?
- [ ] Cannibalisation : deux pages sur la même intention ?
- [ ] Cocon : les rubriques correspondent-elles à des intentions de
      visiteurs (carte de la demande), et chaque page a-t-elle un rôle
      distinct ? Voir [french-practitioners.md](french-practitioners.md)
      (CLAIMED).
- [ ] Définition canonique de l'entité (nom et description) identique sur
      le site et les profils externes (CLAIMED, D2).
- [ ] Glossaire : le site emploie-t-il un vocabulaire que ses visiteurs
      cherchent (sigles, termes techniques) ? Si oui, proposer un lexique
      (`glossary_check.py suggest`). S'il existe : définitions originales,
      une URL propre seulement pour un terme qui a sa propre intention,
      première mention des articles liée à la définition
      (`glossary_check.py audit --site`). SEO : ESTABLISHED (règles
      générales) ; citations IA : non démontré. Voir
      [glossary.md](glossary.md).
- [ ] Mots-clés sous-exploités (avant de choisir les requêtes), voir
      [keyword-research.md](keyword-research.md) : matrice de suggestions,
      SERP lues, notation, preuve propre exigée par page.
- [ ] Formats de contenu (avant d'en planifier), voir
      [content-formats.md](content-formats.md) :
  - chaque format prévu répond à une intention de la carte de la demande,
    et suit la ligne de la table de décision pour ce type de site ;
  - test, comparatif ou classement : preuve de première main visible
    (photos, mesures, protocole), avantages et inconvénients, critères
    de comparaison (reviews system, ESTABLISHED) ;
  - fiche technique ou tableau : chaque valeur a une source et une date,
    et le tableau est en HTML (`<table>`), pas en image ni en PDF ;
  - données originales ou statistiques : méthode, période, taille de
    l'échantillon et date publiées sur la page ;
  - FAQ : questions réelles, réponses visibles dans le HTML ; aucun gain
    de rich result attendu (supprimé le 2026-05-07) ;
  - aucune série de pages par variante de requête, de ville ou de
    produit sans contenu propre (*scaled content abuse*, *doorways*) ;
    aucun avis recopié du fabricant (*thin affiliation*) ;
  - calculateur ou outil : le résultat et l'explication existent aussi
    en texte dans le HTML initial.
- [ ] Contenu non rafraîchi depuis > 12 mois sur un sujet qui bouge ? (mettre
      à jour le fond, pas seulement la date)
- [ ] Pages « vides » indexables (liste sans résultat, rubrique sans
      contenu) : les passer en `noindex` tant qu'elles sont vides.

## Signaux de confiance
- [ ] Page À-propos réelle ; mentions légales complètes (éditeur,
      hébergeur, immatriculation, contact).
- [ ] Auteur identifiable, page auteur, `author.url` dans le JSON-LD.
- [ ] URLs de politiques éditoriales (`correctionsPolicy`,
      `diversityPolicy`...) pointant vers une page qui contient vraiment
      cette politique.
- [ ] NAP cohérent entre site, Google Business Profile et annuaires (local).
- [ ] Date de mise à jour visible ; chiffres publics datés et exacts.

## Données externes (accès requis)
- [ ] Search Console : pages en impressions sans clic → title/description.
- [ ] Search Console : pages attendues sans impression → indexation.
- [ ] CrUX : Core Web Vitals terrain (`crux_report.py`) ; pas de données =
      trafic insuffisant, pas un problème de performance.
- [ ] Journaux serveur (si le propriétaire les fournit) : `crawler_logs.py`
      — crawlers réels et usurpés, 5xx/429 servis à Googlebot ou bingbot,
      URLs du sitemap jamais récupérées, hits des fetchers « utilisateur »
      (ChatGPT-User, Perplexity-User…). Voir [automation.md](automation.md).
- [ ] IndexNow : clé publiée **à la racine** (vérifiée par `run_audit.py`
      si la clé est dans l'environnement), URLs récentes soumises.
- [ ] Citations IA : relevé manuel daté de 10 à 20 questions réelles
      (ligne de base, puis mensuel) — facultatif, CLAIMED (D1, D4). Un
      panel par API (OpenAI, Perplexity, Anthropic) n'est qu'un indicateur
      approché ; jamais par grounding Gemini ni scraping de Google
      (interdit par leurs conditions, [automation.md](automation.md)).

## Décisions à remonter (ne jamais trancher seul)
- [ ] Ouvrir ou fermer les crawlers IA, par rôle (recherche, utilisateur,
      entraînement) ; opt-out IA Google.
- [ ] Migration d'URLs, sous-domaine vs sous-répertoire.
- [ ] Suppression ou désindexation de pages existantes.
