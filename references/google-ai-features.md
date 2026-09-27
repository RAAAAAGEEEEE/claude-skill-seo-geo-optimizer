# Google : AI Overviews, AI Mode, Discover, Actualités, Search Console

Revu le 2026-09-27. Tout est **ESTABLISHED** (documentation ou blog Google)
sauf mention. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

## AI Overviews et AI Mode

| Fait | Source (date) |
|---|---|
| Lancés **en France le 2026-07-22** (mobile, desktop, app Google) | [Google France](https://blog.google/intl/fr-fr/nouveautes-produits/explorez-obtenez-des-reponses/recherche-ia-apercus-mode/) |
| Pour être lien source : page indexée et éligible à un extrait. Aucune autre exigence technique, aucun fichier IA, aucun balisage spécial | [AI features](https://developers.google.com/search/docs/appearance/ai-features) (maj 2025-12-10) |
| Guide « Optimizing your website for generative AI features » : l'optimisation pour l'IA « reste du SEO ». Inutiles pour Google Search : llms.txt et fichiers spéciaux, découpage en petits morceaux (« chunking »), réécriture pour l'IA, mentions inauthentiques ; données structurées non requises | [guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (publié 2026-05-15, maj 2026-07-10) |
| Créer une page par requête « fan-out » pour manipuler les réponses IA relève de la politique **scaled content abuse** | même guide |
| Contrôles : robots.txt de `Googlebot`, puis `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`. `nosnippet` empêche aussi l'usage comme entrée directe | AI features ; [robots meta](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) (maj 2026-03-24) |
| `Google-Extended` ne retire **pas** un site des AI Overviews / AI Mode | [common crawlers](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) (maj 2026-07-14) |
| **Réglage « Search generative AI »** dans Search Console (Paramètres) : Inclure (défaut) / Exclure / Hériter. Mondial depuis le **2026-08-31**. Exclure = plus de liens ni d'usage comme entrée dans AI Overviews, AI Mode et AI Overviews de Discover, sans effet sur le classement ailleurs ni sur l'entraînement ; effet en 1-2 jours | [aide Search Console](https://support.google.com/webmasters/answer/16908024), [blog Google](https://blog.google/products-and-platforms/products/search/new-controls-website-owners/) (2026-06-03, maj 2026-08-31) |
| Être « inclus » dans ce réglage est désormais une condition d'éligibilité | guide d'optimisation (2026-07-10) |

Règle d'audit : sur un site qui ne se voit pas dans les réponses IA de
Google, vérifier **dans cet ordre** : indexation, `nosnippet`/`max-snippet`,
réglage Search Console « Search generative AI ». Jamais Google-Extended.

## Mesure dans Search Console

- AI Overviews et AI Mode sont comptés dans le type **Web** du rapport
  Performances (AI Mode depuis le 2025-06-16). Un AI Overview occupe une
  position ; tous ses liens prennent cette position ; une relance dans AI
  Mode compte comme nouvelle requête
  ([aide](https://support.google.com/webmasters/answer/7042828)).
- Rapports **« Generative AI performance »** (Search et Discover) : annoncés
  le 2026-06-03, tous les sites depuis le 2026-08-31. **Impressions
  seulement**, par page, pays, appareil, date, heure. Pas documentés dans
  l'API au 2026-09-27 ([blog](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)).
- Filtre « Web: multimodal » (Lens, Circle to Search) depuis le 2026-09-24.
- API Search Analytics (réf. maj 2026-08-11) : `type` = web, discover,
  googleNews, news, image, video ; `dataState` = final, all, hourly_all ;
  25 000 lignes max par requête. Utilisé par
  [`../scripts/gsc_report.py`](../scripts/gsc_report.py).
- Fonctions 2025-2026 : données horaires API (2025-04-09), nouveau rapport
  Insights (2025-06-30), groupes de requêtes (2025-10-27), annotations
  (2025-11-17), filtre requêtes de marque (2025-11-20), vues
  hebdo/mensuelles (2025-12-10), propriétés réseaux sociaux (2026-07-07).
- Anomalie : impressions sur-comptées du 2025-05-13 au 2026-04-27 (clics non
  affectés) ; la correction peut ressembler à une baisse
  ([aide](https://support.google.com/webmasters/answer/6211453)). À citer
  avant toute comparaison annuelle.

## Sources préférées (Top Stories)

- Lancé le 2025-08-12 (US, Inde), **toutes langues et pays depuis le
  2026-04-30**, donc France et français
  ([doc](https://developers.google.com/search/docs/appearance/preferred-sources), maj 2026-09-18).
- Depuis le 2026-05-27, un site choisi porte un libellé « Preferred » dans
  AI Overviews et AI Mode (s'il est « inclus » dans le réglage IA).
- Domaines et sous-domaines seulement, pas de sous-répertoire.
- Promotion : lien `https://www.google.com/preferences/source?q=exemple.fr`,
  ou bouton JavaScript officiel depuis le 2026-08-20 (script
  `news.google.com/swg/js/v1/publisher.js` : c'est un appel tiers, à arbitrer
  sur un site sans script externe).
- Chiffres Google non audités : clic deux fois plus probable, 600 000+
  sources choisies (2026-08-20) — ESTABLISHED comme déclaration, pas comme
  mesure indépendante.

## Discover

- Aucune balise requise : page indexée + politiques de contenu respectées
  ([doc](https://developers.google.com/search/docs/appearance/google-discover), maj 2026-03-09).
- Image : ≥ 1200 px de large, > 300 000 pixels, 16:9 recommandé,
  `max-image-preview:large`, image déclarée en schema.org ou `og:image`, pas
  de logo. Google utilise schema.org **et** `og:image` pour la vignette
  depuis le 2026-03-02.
- Depuis le 2026-02-05 : éviter clickbait et sensationnalisme. Core update
  Discover de février 2026 (US anglais seulement ; extension annoncée, non
  constatée au 2026-09-27).
- Fonction « Suivre » retirée (doc supprimée le 2025-11-19).
- Politiques : dates, auteur, éditeur et contact visibles ; violations
  répétées = inéligibilité à Discover.

## Google Actualités / Top Stories

- Aucune soumission : inclusion automatique si les règles Google News sont
  respectées. Publisher Center ne crée plus de publication depuis le
  2024-04-25 et n'utilise plus les flux soumis depuis mars 2025
  ([annonces](https://support.google.com/news/publisher-center/announcements/10146168)).
- Bloquer `Googlebot-News` retire de Google Actualités sans toucher Search.
- Sitemap News : articles des 2 derniers jours seulement.

## Mises à jour de classement récentes

Core update de mai 2026 (terminée le 2026-06-02) ; spam updates de juin
(24-26), août (18-21) et septembre 2026 (démarrée le 2026-09-24, en cours)
([Search Status Dashboard](https://status.search.google.com/)). Politique
« site reputation abuse » : plus d'actions manuelles pour les utilisateurs de
l'EEE depuis le 2026-08-30.

## Chiffres « zéro clic » : origine réelle
- « ~65 % » = SparkToro/Similarweb, **année 2020**, publié 2021
  (CLAIMED, méthode publiée, périmé).
- Dernier chiffre : 68,01 % des recherches Google US sans clic vers le web
  ouvert, janvier-avril 2026, hors app Google (SparkToro/Similarweb,
  2026-06-08, CLAIMED, méthode publiée).
- « ~93 % en AI Mode » = Semrush, sessions desktop US mai-juillet 2025
  (CLAIMED, méthode publiée, périmètre étroit). AI Mode = 0,34 % des
  recherches US début 2026 (SparkToro).
- Indépendant : Pew Research (mars 2025, 900 adultes US, 68 879
  recherches) — clic sur un résultat 8 % avec résumé IA contre 15 % sans ;
  1 % de clic sur une source du résumé (SUPPORTED,
  [Pew, 2025-07-22](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/)).
Ne jamais citer ces chiffres sans leur périmètre et leur date.
