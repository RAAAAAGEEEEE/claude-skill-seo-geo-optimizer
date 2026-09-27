# Checklist — uniquement ce que les scripts ne peuvent PAS vérifier

Revu le 2026-09-27.

Tout ce qui est automatisable en est retiré. Ne pas revérifier à la main ce
que `generate_report.py` contrôle (HTTP, redirections, noindex/nosnippet,
title, description, canonical, H1, lang, JSON-LD, hreflang, Search Console)
ni ce que `check_ai_access.py` contrôle (robots.txt, accès par crawler).

## Avant de commencer
- [ ] `python scripts/check_ai_access.py <url>` exécuté — si un crawler de
      recherche/citation est bloqué, le traiter avant tout le reste.
- [ ] `python scripts/generate_report.py --urls urls.txt --out-prefix audit`
      exécuté ; ce qui suit le complète.

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
- [ ] IndexNow : clé publiée **à la racine**, URLs récentes soumises.

## Décisions à remonter (ne jamais trancher seul)
- [ ] Ouvrir ou fermer les crawlers IA, par rôle (recherche, utilisateur,
      entraînement) ; opt-out IA Google.
- [ ] Migration d'URLs, sous-domaine vs sous-répertoire.
- [ ] Suppression ou désindexation de pages existantes.
