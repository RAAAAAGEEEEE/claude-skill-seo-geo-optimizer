# Formats de contenu : ce que Google classe et ce que les moteurs IA citent

Revu le 2026-09-28. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
« maj » = date « Last updated » de la page ; « consulté » = page sans date,
lue le 2026-09-28.

À utiliser quand on **planifie** du contenu : nouvelles pages, refonte
éditoriale, choix entre deux formats pour une même intention. Ce fichier
ne remplace ni la carte de la demande
([french-practitioners.md](french-practitioners.md), B2) ni le registre des
preuves ([evidence.md](evidence.md)).

## Verdict

1. **Aucun format n'est récompensé en soi par Google** (ESTABLISHED). Google
   ne fixe aucun nombre de mots, n'exige aucun balisage pour ses fonctions
   IA, et range un contenu banal (son exemple : « 7 Tips for First-Time
   Homebuyers ») parmi le *commodity content*. Ce qui compte pour tous les
   formats : information originale, expérience de première main, sources
   claires, auteur identifiable.
2. **Tests, comparatifs et classements** relèvent d'un système dédié, le
   *reviews system*, qui s'applique au français et évalue surtout page par
   page (ESTABLISHED). Ses critères sont publiés : ce sont eux qu'un audit
   vérifie.
3. **Les parts de citation par format** (comparatifs, listes, guides…)
   viennent d'études de vendeurs d'outils (CLAIMED). Elles varient selon
   l'intention de la requête, le moteur, la période et la méthode, et se
   contredisent sur les comparatifs et les FAQ. Elles orientent un choix, elles ne
   fondent pas une priorité.
4. **Le format suit l'intention et la preuve détenue.** Un site qui n'a pas
   testé un produit ne publie pas de test ; un site sans donnée propre ne
   publie pas d'observatoire. Publier le format sans la preuve, c'est
   produire du contenu banal, voire du *scaled content abuse*.

## Ce que Google dit (ESTABLISHED)

| Affirmation | Source (date) |
|---|---|
| Questions d'auto-évaluation : le contenu apporte-t-il « original information, reporting, research, or analysis » ? Sources claires, expertise visible, page qu'on voudrait garder ou partager | [helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) (maj 2025-12-10) |
| Pas de nombre de mots préféré ; ne pas changer la date d'une page pour la faire paraître fraîche sans changement substantiel ; « Who, How, Why » (auteur évident, méthode de production, finalité) | idem |
| Fonctions IA : le contenu unique et non banal comptera plus que toute autre suggestion. Exemple de Google : un test de première main apporte un point de vue propre, un résumé de contenus existants ne fait que répéter | [guide IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (publié 2026-05-15, maj 2026-07-10) |
| Même guide : organiser en paragraphes et sections avec des titres clairs ; ajouter images et vidéos de qualité ; pas de découpage en petits morceaux, pas de fichier ni de balisage spécial IA ; une page par variante de requête ou par sous-requête *fan-out* = *scaled content abuse* | idem |
| Même guide : pour les produits et les commerces, flux Merchant Center et fiche Google Business Profile | idem |
| *Reviews system* : récompense « insightful analysis and original research » ; porte sur les produits, services, médias, et sur « single reviews, comparisons, and ranked lists » ; évaluation surtout par page, par site au-delà d'un volume important ; langues dont le français ; mises à jour non annoncées à part | [reviews system](https://developers.google.com/search/docs/appearance/reviews-system) (maj 2025-12-10) |
| Bonnes pratiques des tests : point de vue de l'utilisateur, preuves de sa propre expérience (images, audio, liens), mesures quantitatives, ce qui distingue le produit de ses concurrents, évolution depuis le modèle précédent, avantages et inconvénients tirés de sa propre recherche, liens vers plusieurs vendeurs, classements assez fournis pour tenir seuls | [write high-quality reviews](https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews) (maj 2025-12-10) |
| *Thin affiliation* : descriptions et avis recopiés du marchand sans contenu original ni valeur ajoutée ; *scaled content abuse* (dont l'IA générative sans valeur ajoutée) ; *doorways* : pages créées pour des requêtes similaires | [spam policies](https://developers.google.com/search/docs/essentials/spam-policies) (maj 2026-08-28) |
| Dates : date de publication et de mise à jour visibles, identiques au balisage (`datePublished`, `dateModified`) ; ne pas afficher d'autres dates qui prêtent à confusion | [dates](https://developers.google.com/search/docs/appearance/publication-dates) (maj 2025-12-10) |
| Contenu produit avec l'IA : admis s'il apporte de la valeur ; la production de masse sans valeur relève du spam | [contenu IA](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) (maj 2025-12-10) |

### Données structurées encore utiles selon le format (ESTABLISHED)

Galerie Google (maj 2026-06-15) : 25 fonctionnalités, dont Article,
Breadcrumb, Dataset, Discussion forum, Organization, Product, Profile page,
Q&A, Review snippet, Software app, Video. Détail et gabarits :
[schema-templates.md](schema-templates.md).

| Format | Balisage | Effet documenté |
|---|---|---|
| Test d'un produit | `Product` + `Review` (auteur, note, objet) ; `positiveNotes`/`negativeNotes` pour les avantages et inconvénients d'une page de test éditorial | Extrait d'avis et avantages/inconvénients ([product](https://developers.google.com/search/docs/appearance/structured-data/product), maj 2025-12-10 ; [review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet), maj 2026-09-08). Jamais d'étoiles sur sa propre entreprise ; avis incités non déclarés interdits |
| Fiche produit sans achat | `Product` avec `review` ou `aggregateRating` ou `offers` | *Product snippet* ; sans ces propriétés, balisage d'entité seulement |
| Logiciel, application | `SoftwareApplication` | Rich result *Software app* ([doc](https://developers.google.com/search/docs/appearance/structured-data/software-app), maj 2026-09-08) |
| Article, guide, tutoriel, chronologie | `Article` avec `author.url`, `datePublished`, `dateModified` | Compréhension de l'auteur et des dates ([Article](https://developers.google.com/search/docs/appearance/structured-data/article), maj 2026-09-08) |
| Page auteur, À propos | `ProfilePage` avec `mainEntity` (`Person` ou `Organization`) | Prévu pour « an author page on a news site » ([ProfilePage](https://developers.google.com/search/docs/appearance/structured-data/profile-page), maj 2026-09-08) |
| Jeu de données, observatoire | `Dataset` | **Dataset Search seulement**, plus Google Search (2025-11-05) ([Dataset](https://developers.google.com/search/docs/appearance/structured-data/dataset), maj 2026-09-08) |
| FAQ | `FAQPage` | **Aucun rich result depuis le 2026-05-07.** La FAQ reste utile comme texte visible |
| Tutoriel | `HowTo` | Aucun rich result depuis 2023 |
| Définitions | `DefinedTerm` | Aucun rich result ([glossary.md](glossary.md)) |
| Calculateur, chronologie, changelog | aucun type dédié dans la galerie | — |

## Ce que mesurent les études de citations IA

Lues entre le 2026-09-27 et le 2026-09-28. La plupart des études sont
faites en anglais, aux États-Unis, par des vendeurs d'outils : elles
mesurent des **corrélations**, pas des causes. Deux métriques se côtoient et
ne se comparent pas :
- la **part des citations** : sur 100 citations, combien vont à tel format ;
- le **taux de citation** : sur 100 pages d'un format, combien sont citées.

### Déclarations des moteurs (ESTABLISHED)

| Déclaration | Source (date) |
|---|---|
| Google : contenu unique, non banal, de première main ; sections et titres clairs ; images et vidéo. Aucun format nommé : ni liste, ni comparatif, ni FAQ | [guide IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (maj 2026-07-10) ; [blog Google](https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search) (2025-05-21) |
| Microsoft : paires question-réponse reprenables telles quelles ; listes, étapes numérotées et **tableaux comparatifs** pour les requêtes pratiques et les comparaisons de fonctionnalités ; réponses courtes compréhensibles hors contexte. À éviter : réponses cachées dans des onglets, ou seulement dans des images ou des PDF | [Microsoft Advertising](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers) (2025-10-08) |
| Bing : l'index sert des faits vérifiables à la provenance claire, plus seulement des pages ; la fraîcheur est critique ; le *grounding* pèse la force de la preuve | [Bing](https://blogs.bing.com/search/May-2026/Evolving-role-of-the-index-From-ranking-pages-to-supporting-answers) (2026-05-06) |
| OpenAI, Perplexity, Anthropic : aucun critère de format publié. Les pages d'aide d'OpenAI répondent 403 (**non vérifié**) | consultés le 2026-09-28 |

Google et Bing divergent sur la forme. Google demande de ne pas réécrire ni
découper pour l'IA ; Bing recommande des blocs question-réponse et des
tableaux. Les deux convergent sur le fond : des faits sourcés, datés,
visibles dans le HTML.

### Études indépendantes (SUPPORTED)

| Constat | Source (date) |
|---|---|
| Ajouter à un passage des citations de sources et des statistiques : jusqu'à +41 % de visibilité dans un moteur simulé, +37 % sur Perplexity. Le bourrage de mots-clés fait moins bien que le témoin. Ce sont des réécritures de passages, pas des types de pages | [Aggarwal et al., KDD](https://arxiv.org/abs/2311.09735) (2024-06-28) |
| **Contredit la ligne précédente** : la plupart des méthodes de réécriture « conversationnelle » sont inefficaces ou nuisibles. Le SEO classique (être mieux placé dans ce que le LLM reçoit) l'emporte. Le gain baisse quand tout le monde les adopte | [C-SEO Bench, NeurIPS D&B](https://arxiv.org/abs/2506.11097) (2025-06-06, rév. 2025-10-20) |
| Biais « systématique » des moteurs IA vers les médias tiers, au détriment des sites de marque et des réseaux sociaux (résumé seulement) | [Chen et al.](https://arxiv.org/abs/2509.08919) (2025-09-10) |
| 21 143 citations, 18 151 pages : les pages les plus reprises sont plus longues, plus structurées et riches en éléments extractibles (définitions, chiffres, comparaisons, étapes). Pas de chiffre par type de page dans le résumé | [Zhang et al.](https://arxiv.org/abs/2604.25707) (2026-04-28) |
| 11 500 requêtes : les sources diffèrent fortement d'un moteur à l'autre (Jaccard < 0,2) | [Grossman et al., SIGIR](https://arxiv.org/abs/2604.27790) (2026-04-30) |
| Résumés IA de Google : Wikipedia, YouTube et Reddit font 15 % des liens (17 % dans les résultats classiques) ; les sites .gov 6 % (2 %) | [Pew](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/) (2025-07-22) |
| 366 000 citations : 9 % vont à des médias d'information, concentrées sur quelques titres ; les sources peu fiables sont rarement citées | [Yang](https://arxiv.org/abs/2507.05301) (2025-07-07) |

### Études de vendeurs (CLAIMED)

| Constat | Méthode | Source (date) |
|---|---|---|
| 1,06 M de citations (ChatGPT, AI Mode, Perplexity) en 11 types : listicle 21,9 %, article 16,7 %, fiche produit 13,7 %, page catégorie 11,3 %, discussion 7,5 %, how-to 6,2 %, accueil 5,3 %, profil 5,1 %, **comparatif 2,2 %**, « alternatives » 0,3 %. Par intention : informationnelle, articles 45,5 % ; commerciale, listicles 40,9 % ; transactionnelle, fiches produit 24,9 %. L'intention pèse plus que le moteur | critères de classement non publiés | [Wix / Peec AI](https://www.wix.com/studio/ai-search-lab/research/content-types-most-cited-by-llms) (2026-03-23) |
| Prompts « best X » : les listes en format blog font 43,8 % des pages citées par ChatGPT ; 79 % ont été mises à jour dans l'année ; aucun effet négatif observé de l'auto-promotion | publiée | [Ahrefs](https://ahrefs.com/blog/best-lists-research/) (2025-12-04) |
| Quand un AI Overview cite la liste « best » d'une marque, cette marque n'est pas recommandée dans 69 % des cas (224 sur 323). Sept sites SaaS riches en listicles auto-promotionnels ont perdu 29 à 49 % de visibilité organique après décembre 2025 (corrélation, de l'aveu de l'autrice) | publiée, petit échantillon | [Lily Ray](https://lilyraynyc.substack.com/p/why-calling-yourself-the-best-could) (2026-06-17) ; [Lily Ray](https://lilyraynyc.substack.com/p/is-google-finally-cracking-down-on) (2026-02-03) |
| Contenu produit (fiches, « best of », comparatifs face à face) : 46 à 70 % des citations, 70 % en bas d'entonnoir ; avis et forums 3 à 10 % ; blogs 3 à 6 % | 768 000 citations, 12 semaines | [XFunnel](https://www.xfunnel.ai/blog/what-content-type-ai-engines-like) (2025-04-08) |
| Prompts contenant une marque : avis et preuve sociale 57 %, annuaires et pages de référence 17 %, fiches produit 12 %, **FAQ 0,4 %** | 23 387 sources, 240 prompts | [Omniscient / Peec AI](https://beomniscient.com/blog/content-types-cited-in-llms/) (2026-01-20) |
| ChatGPT cite plus souvent une page dont le titre est proche de la question et l'URL en langage naturel ; Reddit est très souvent récupéré mais non cité | publiée ; période incohérente sur la page | [Ahrefs](https://ahrefs.com/blog/why-chatgpt-cites-pages/) (2026-04-15) |
| Domaines les plus cités par ChatGPT (US) : Reddit 16,8 %, Wikipedia 7,0 %, Consumer Reports 3,7 % | outil propriétaire | [Ahrefs](https://ahrefs.com/blog/most-cited-domains-in-chatgpt/) (2026-09-02) |
| « Taux de citation » : fiches produit 68,5 %, comparatifs 62,8 % (95 % sur ChatGPT). FAQ, statistiques, tableaux, bios d'auteur et dates corrélés aux citations | métrique mal définie | [HubSpot](https://blog.hubspot.com/marketing/content-format-types-that-earn-citations) (2026-06-03) |

Recoupement des citations avec le top 10 de Google : voir
[evidence.md](evidence.md) (études en conflit).

### Conflits à dire au propriétaire

1. **Comparatifs** : 2,2 % des citations (Wix/Peec) contre 95 % de « taux
   de citation » sur ChatGPT (HubSpot). Les métriques diffèrent ; aucune ne
   permet de conclure qu'un comparatif « gagne ».
2. **Listes « best »** : très citées sur les requêtes commerciales. Mais
   être cité n'est pas être recommandé (69 % d'exclusion), et une baisse
   organique est observée chez des sites qui en publient en masse.
   **Aucune déclaration de Google** ne vise ces listes, hors les critères
   du reviews system.
3. **Réécrire pour l'IA** : +41 % (GEO, moteur simulé) contre inefficace
   (C-SEO Bench). Google demande de ne pas le faire.
4. **Reddit, Wikipedia** : parts très variables selon la période, l'outil et
   le moteur. Ce sont des sources tierces : y être présent relève des
   mentions (skill `SEO`), pas de ce skill.

### Formats sans aucune donnée publiée (au 2026-09-28)

- Chronologies et historiques, changelogs, calculateurs et outils, fiches
  techniques : aucune étude.
- Tableaux comparatifs : la recommandation de Microsoft et une corrélation
  HubSpot.
- Pages auteur : une corrélation HubSpot.
- Définitions : Zhang et al. les rangent parmi les éléments extractibles,
  sans chiffre par page ([glossary.md](glossary.md)).

**Non vérifié** :
- Growth Memo, « The science of how AI picks its sources » (2026-03-23),
  derrière un paywall : ne pas reprendre les chiffres qui en circulent ;
- rapport complet Semrush AI Visibility Index 2026 ;
- Search Engine Land et aide OpenAI (403).

## Fiche par format

Chaque fiche dit : ce que Google documente, ce que disent les études, et la
condition sans laquelle le format ne vaut pas d'être publié.

| # | Format | Google (ESTABLISHED) | Études de citation | Condition pour publier | Risque |
|---|---|---|---|---|---|
| F1 | **Fiche entité / fiche produit** avec tableau de caractéristiques sourcées | Règles générales ; `Product` (snippet si avis, note ou offre) ou `SoftwareApplication` ; Merchant Center si vente | Fiches produit : 13,7 % des citations, 24,9 % en transactionnel (CLAIMED, Wix/Peec) ; Bing veut des faits datés à la provenance claire (ESTABLISHED) | Chaque valeur a une source (fabricant, norme, mesure maison) et une date de vérification ; tableau en `<table>` HTML ; au moins une information que la fiche du fabricant n'a pas (contexte, comparaison, historique) | Fiche recopiée du fabricant = *thin affiliation* ; milliers de fiches vides = *scaled content abuse* |
| F2 | **Comparatif « X vs Y »** | *Reviews system* (« comparisons ») ; critères des tests : ce qui distingue, pour quels usages | 2,2 % des citations (Wix/Peec) contre 95 % de « taux de citation » sur ChatGPT (HubSpot) : **conflit** ; Microsoft recommande les tableaux comparatifs | Critères explicites, mêmes critères pour chaque produit, données sourcées ; verdict par usage, pas un gagnant unique ; seulement pour des paires que les visiteurs comparent vraiment | Toutes les paires possibles générées = *doorways* / *scaled content abuse* |
| F3 | **Classement « meilleurs X »** | *Reviews system* (« ranked lists ») : chaque entrée doit tenir seule ; preuve de première main | 21,9 % des citations, 40,9 % en commercial (Wix/Peec) ; 43,8 % sur prompts « best » (Ahrefs) ; mais la marque qui s'auto-classe n'est pas recommandée dans 69 % des cas (Ray) — tout CLAIMED | Produits réellement testés ou comparés sur des données publiées ; méthode de sélection visible ; divulgation si le site vend l'un des produits ou touche une commission | Liste auto-promotionnelle rafraîchie sans changement réel : baisse organique observée (CLAIMED) et date trompeuse (ESTABLISHED) |
| F4 | **Guide d'achat** | *Reviews system* et questions d'auto-évaluation : aider à décider, critères, usages | Pas de catégorie propre ; rangé dans « article » ou « listicle » selon les études | Critères de choix expliqués avec leurs ordres de grandeur sourcés ; renvoi vers les fiches (F1) et les tests (F5) du site ; mis à jour quand l'offre change | Guide générique (« 7 conseils… ») = *commodity content* (exemple de Google) |
| F5 | **Test de première main** | Critères publiés : preuves de sa propre expérience (photos, mesures), avantages et inconvénients, comparaison au modèle précédent et aux concurrents ; `Review` + `positiveNotes`/`negativeNotes` | Avis et preuve sociale : 57 % sur prompts de marque (CLAIMED, Omniscient) ; Google cite le test de première main comme exemple de contenu non banal | Le produit a vraiment été utilisé ou mesuré, et la page le montre (photos d'origine, protocole, conditions, date) ; auteur nommé | Test sans usage réel ; avis incités non déclarés (interdits) ; étoiles sur sa propre entreprise |
| F6 | **Données originales, observatoire, statistiques** | « Original information, reporting, research, or analysis » (question d'auto-évaluation) ; `Dataset` = Dataset Search seulement | Statistiques et citations ajoutées : +41 % en moteur simulé (SUPPORTED, GEO) mais contredit par C-SEO Bench ; Bing : faits vérifiables et frais (ESTABLISHED) | Méthode, source, période, taille de l'échantillon et date publiées sur la page ; données téléchargeables si possible ; mise à jour datée | Chiffres recopiés d'ailleurs sans valeur ajoutée ; chiffre non sourcé repris en boucle ([data-hygiene.md](data-hygiene.md)) |
| F7 | **Chronologie / historique** | Règles générales ; `Article` avec dates | **Aucune donnée** | Chaque date a une source ; la chronologie apporte un regroupement que d'autres pages n'offrent pas ; dates des événements distinctes de la date de mise à jour | Compilation d'autres sites sans apport = contenu banal |
| F8 | **Tutoriel / how-to** | Règles générales ; `HowTo` sans rich result depuis 2023 ; images et vidéo encouragées | how-to : 6,2 % des citations (Wix/Peec) ; Microsoft : étapes numérotées | Étapes réellement exécutées, prérequis, résultat attendu, captures d'origine, version du produit et date | Tutoriel générique réécrit depuis la documentation officielle |
| F9 | **FAQ en texte visible** | Rich result supprimé le 2026-05-07 ; le balisage doit refléter le visible | FAQ : 0,4 % des citations sur prompts de marque (Omniscient) ; corrélée aux citations (HubSpot) ; Microsoft : paires question-réponse — **conflit** | Questions réellement posées (support, Search Console), réponses courtes et exactes, dans le HTML (pas seulement dans un accordéon rendu en JavaScript), sur la page du sujet | Page FAQ fourre-tout qui duplique les autres pages ; FAQ générée en masse |
| F10 | **Définitions / glossaire** | Voir [glossary.md](glossary.md) : utile sous conditions ; `DefinedTerm` sans rich result | Définitions = éléments extractibles (SUPPORTED, Zhang et al., sans chiffre par page) ; 47 % des requêtes « définition » ont un AI Overview (CLAIMED) : risque de zéro clic | Définitions originales, liées depuis les articles | Définitions recopiées ou générées en masse |
| F11 | **Changelog / journal des mises à jour** | Règles générales ; ne pas changer une date sans changement réel ; `dateModified` exact | **Aucune donnée** ; Bing insiste sur la fraîcheur (ESTABLISHED) | Chaque entrée datée et précise (ce qui a changé, pourquoi) ; utile pour un SaaS, une base de données ou un observatoire | Journal fictif ou automatique qui simule la fraîcheur |
| F12 | **Calculateur / outil** | Aucune règle propre ; le contenu doit être dans le HTML pour être lu | **Aucune donnée** | La méthode de calcul, les hypothèses et un exemple chiffré sont écrits en texte dans le HTML initial ; sources des coefficients | Outil en JavaScript seul : invisible pour les crawlers qui ne rendent pas le JS ; déclinaisons par ville ou par valeur = *doorways* |
| F13 | **Page auteur, À propos, méthodologie** | « Who, How, Why » ; `author.url` ; `ProfilePage` prévu pour une page auteur ; politiques éditoriales exactes ([eeat-news.md](eeat-news.md)) | Bios d'auteur corrélées aux citations (CLAIMED, HubSpot) ; profils : 5,1 % des citations (Wix/Peec) | Personne réelle, expérience vérifiable, liens vers ses profils ; page méthodologie qui décrit vraiment comment les tests et les données sont faits | Auteur fictif ou expertise inventée |

## Table de décision par type de site

Lecture : **cœur** = format central pour ce type de site, à planifier en
premier ; **si** = utile sous la condition donnée ; **rare** = seulement
pour une intention précise et démontrée ; **non** = à éviter. Le choix vient
de la documentation de Google et de la cohérence avec le type de site
(jugement du skill, **CLAIMED**). Les études de citation ne l'orientent
qu'à la marge : elles ne distinguent pas les types de sites.

| Format | Référence / base de produits | Média / éditorial | SaaS / logiciel | E-commerce | Local / service | Données / observatoire |
|---|---|---|---|---|---|---|
| F1 Fiche entité + caractéristiques sourcées | **cœur** | rare | si : fiches des fonctions ou intégrations | **cœur** (Merchant Center) | si : une fiche par prestation réelle | si : fiche par série de données |
| F2 Comparatif « X vs Y » | si : paires réellement cherchées, données de la base | si : test des deux | si : honnête face aux concurrents, critères publiés | si | rare | si : comparaison de séries |
| F3 Classement « meilleurs X » | si : critères tirés des données, méthode publiée | si : produits testés | **non** s'il s'auto-classe premier | si : divulgation, produits réellement vendus et évalués | non | si : classement calculé, méthode publiée |
| F4 Guide d'achat | si : relié aux fiches | **cœur** | rare | **cœur** | si : « comment choisir un prestataire » | rare |
| F5 Test de première main | si : le site teste vraiment | **cœur** si le média teste | rare | si : tests internes ou avis clients vérifiés | non | non |
| F6 Données originales, statistiques | **cœur** : statistiques calculées sur la base | si : enquête propre | si : données d'usage agrégées et anonymisées | si | rare | **cœur** |
| F7 Chronologie / historique | si : histoire d'une catégorie, dates sourcées | si | rare | rare | rare | si : évolution des séries |
| F8 Tutoriel / how-to | si | si | **cœur** : documentation et tutoriels | si : usage et entretien | si | si : comment lire ou réutiliser les données |
| F9 FAQ visible | si : sur la page du sujet | rare | si : support réel | si : sur la fiche | **cœur** : questions réelles des clients | si |
| F10 Définitions / glossaire | **cœur** si vocabulaire technique | si | si | rare | rare | si : définitions des indicateurs |
| F11 Changelog | si : journal des ajouts et corrections de la base | rare : corrections d'articles | **cœur** | rare | non | **cœur** : versions des données |
| F12 Calculateur / outil | si : méthode écrite en HTML | rare | si | si | si : devis indicatif, hypothèses écrites | si |
| F13 Auteur, À propos, méthodologie | **cœur** : méthodologie des données | **cœur** | si | si | **cœur** : À propos, mentions légales | **cœur** : méthodologie |

Quel que soit le type de site :
- une page par intention, jamais une page par variante de requête, de
  ville, de modèle ou de paire sans contenu propre ;
- aucun volume cible : Google n'en fixe pas, et le volume sans valeur
  relève du *scaled content abuse* ;
- publier moins de pages, mais chacune avec une preuve que les autres
  n'ont pas.

## Comment s'en servir dans la procédure

1. **Carte de la demande** d'abord (B2 dans
   [french-practitioners.md](french-practitioners.md)) : lister les
   intentions des visiteurs, les regrouper par sujet.
2. Pour chaque intention, prendre la ligne du type de site dans la table.
   Une intention = une page. Jamais une page par variante de requête, de
   ville ou de modèle sans contenu propre.
3. **Vérifier la preuve** que le format exige (colonne « Condition » des
   fiches). Sans elle, écarter le format et le dire au propriétaire.
4. Présenter le plan au propriétaire : il décide des formats, du volume et
   de l'ordre. Rien n'est publié sans relecture humaine
   ([automation.md](automation.md)).
5. Après publication : `run_audit.py` (indexation, maillage, JSON-LD), puis
   Search Console. Le rapport « Generative AI performance » de Google donne
   les impressions par page ; « AI Performance » de Bing donne les citations
   dans Copilot ([google-ai-features.md](google-ai-features.md),
   [automation.md](automation.md)).
