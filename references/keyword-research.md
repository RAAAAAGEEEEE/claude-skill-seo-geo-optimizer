# Mots-clés sous-exploités d'une niche : repérer et se positionner sans outil payant

Revu le 2026-11-03, complété le 2026-11-08 (section « Compléments de praticiens »). Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
« consultée » = page sans date affichée, lue le 2026-11-03.

À utiliser quand on **choisit** les requêtes à viser avant de planifier des pages. Ce fichier
prolonge « Carte de la demande » et « Lecture de la SERP » de
[french-practitioners.md](french-practitioners.md), qui n'en donnent que le principe, et précède
le choix des formats ([content-formats.md](content-formats.md)). La rédaction des pages retenues
relève du skill `redaction`.

## Principe
Aucune source gratuite ne donne un volume de recherche fiable. La méthode assemble des
**signaux relatifs** (suggestions, Trends, Search Console, lecture de SERP), les croise, et
écarte toute requête où le site n'a pas de **preuve propre** à offrir. Un mot-clé sans demande
visible mais à forte valeur commerciale reste retenu si la concurrence est faible ; un mot-clé
à forte demande sans avantage propre est écarté.

## Limites à écrire dans chaque rapport
| Constat | Niveau | Source (date) |
|---|---|---|
| L'absence de suggestion pour une requête signifie un volume sous un seuil inconnu, pas zéro | CLAIMED | pratique courante, aucune doc officielle trouvée (2026-11-03) |
| Le point d'accès de suggestions (`suggestqueries.google.com/complete/search?client=firefox`) n'est pas une API documentée : usage d'observation, sans garantie de stabilité ni de quota | CLAIMED, non vérifié | observé fonctionnel le 2026-11-03 |
| Les suggestions sont biaisées par la localisation de l'IP et de l'historique : une ville qui revient partout peut refléter l'appelant, pas la demande nationale | CLAIMED, observé | relevé du 2026-11-03 (6 suggestions sur 10 portaient sur un même département sans qu'il soit demandé) |
| Google Trends ne donne que des indices relatifs (0 à 100) sur une période, jamais un volume ; il renvoie 429 aux appels automatisés | CLAIMED / observé | HTTP 429 le 2026-11-03 ; lecture manuelle dans le navigateur de l'utilisateur seulement |
| Un moteur de repli (Bing, autre) donne une idée de la nature des résultats, pas de leur ordre sur Google | observé | à étiqueter « approximation » dans le rapport |
| Scraper les pages de résultats Google est contraire à ses conditions : lire la SERP à la main (navigateur de l'utilisateur) ou par un moteur de recherche web tiers, ne pas bâtir de collecte automatique | ESTABLISHED (principe des conditions) | à revérifier avant toute automatisation |

## Procédure

### 1. Graines (15 min)
Lister 5 à 10 termes dans les mots du **client**, pas du produit : le métier, le besoin, le
problème, la forme de réponse attendue (exemple, modèle, prix, avis, comparatif, alternative,
« sans X », « pas cher »). Ajouter 3 formulations sans le mot évident (synonymes, jargon des
forums).

### 2. Suggestions par expansion
Pour chaque graine, interroger le point d'accès de suggestions avec `hl`, `gl` du marché visé :
- la graine seule ;
- la graine + une lettre de a à z (26 appels) ;
- une **matrice** entité × motif (ex. 30 métiers ou segments × 6 motifs : « <motif> <entité> »),
  en notant pour chaque cellule le nombre de suggestions renvoyées (0 à 10) ;
- le motif + une ville ou région (pour la demande locale, voir le biais ci-dessus).

Règles : pause de 0,3 s entre appels, moins de 300 appels par session, valeurs brutes
conservées dans un fichier daté. Lire la matrice ainsi :
- ligne ou colonne à 8-10 suggestions : demande établie, donc concurrence probable ;
- cellule à 0 sur une colonne où les cellules voisines sont à 5+ : demande trop faible pour
  porter une page seule, ou formulation que personne ne tape ;
- **dérive d'intention** : relire le texte des suggestions. Un motif peut être capté par un
  autre sujet (ex. « exemple site X » suggérant « exemple menu X »). Écarter les cellules
  dont les suggestions ne partagent pas l'intention visée.

### 3. Intentions et questions
Regrouper les suggestions par intention : **info** (comment, pourquoi, combien),
**comparaison** (alternative, vs, avis), **transaction** (création, prix, devis, pas cher),
**inspiration** (exemple, modèle, idée), **navigation** (marque). Compléter à la main, dans le
navigateur de l'utilisateur, par « Recherches associées » et « Autres questions posées » sur
les 5 requêtes les plus prometteuses. Ne pas les automatiser.

### 4. Lecture de la SERP (le test décisif)
Pour chaque requête retenue, lire les 10 premiers résultats et remplir :

| Colonne | Contenu |
|---|---|
| Types de pages | service, guide, comparatif, liste, template, annuaire, forum, place de marché de freelances, dictionnaire |
| Correspondance | la page traite-t-elle l'intention **exacte** ou une intention voisine ? |
| Qualité | première main, preuve, date, longueur utile, sources |
| Autorité | grands éditeurs spécialisés ou petits sites |
| Verdict | faible, moyenne, forte |

Signes de concurrence faible (CLAIMED, praticiens) : résultats hors intention (dictionnaire,
pages de définition), forums et fils de discussion, annuaires, pages de templates ou de
places de marché sans contenu sur le sujet, titres qui ne contiennent pas la requête, pages
sans date ou datées de plus de deux ans. Signes de concurrence forte : grands éditeurs
spécialisés avec correspondance exacte et preuves à jour.

Recouper les pages qui sortent : titre, plan (H2/H3), longueur utile, preuves, FAQ, balisage,
date, liens internes entrants. Noter **ce qui les fait sortir** et **ce qui manque** (donnée
originale, exemples réels, mise à jour, filtre par cas d'usage). La page à créer comble ce
manque ; elle ne copie pas le plan.

### 5. Tendance (si accessible)
Dans le navigateur de l'utilisateur : Google Trends, pays visé, 12 mois, comparaison par
groupes de 5 termes avec un **terme pivot** commun à tous les groupes pour rendre les groupes
comparables. Noter la saisonnalité. Si l'accès échoue (429), écrire « tendance : inconnue ».

### 6. Données propres du site (si le site existe)
Search Console, rapport Performances, 3 derniers mois : requêtes avec impressions mais
position moyenne entre 8 et 30 et peu de clics = sous-exploitées pour **ce** site. C'est le seul
signal de demande réel et gratuit. Sans accès : le dire, ne pas extrapoler.

### 7. Notation
Par mot-clé retenu : **demande** (0 à 3, d'après suggestions et Trends), **intention de
valeur** (0 à 3, proximité d'une action utile pour le site), **concurrence** (0 à 3, 3 =
faible), **avantage propre** (0 à 3, preuve que seul ce site peut montrer). Priorité =
somme ; l'avantage propre à 0 élimine la requête quelle que soit la somme.
Le tableau de sortie porte : mot-clé, intention, signal de demande (+ date du relevé),
concurrence observée (+ moteur utilisé), page existante ou à créer, priorité, preuve exigée.

## Se positionner
1. **Une page par intention, jamais une page par variante.** Regrouper les variantes proches
   (singulier/pluriel, ordre des mots) sur une même page.
2. **Une page n'existe que si la base contient une donnée propre à cette page** (chiffre réel,
   exemple réel, test, tarif relevé). Sans donnée : pas de page, ou `noindex` tant qu'elle est
   vide. Jamais de texte de remplissage varié pour les besoins du gabarit.
3. **Mesurer la ressemblance avant publication** : similarité entre paires de pages du même
   gabarit (phrases communes, indice de Jaccard sur des suites de 5 mots). Aucun seuil officiel
   n'existe : fixer un seuil interne et le noter. Une page dont le texte propre est faible
   reste en `noindex`.
4. **Publier par lots** de 5 à 10 pages, attendre 4 à 6 semaines de données Search Console
   (indexation, impressions, position), puis étendre ce qui a fonctionné. Le délai est une
   pratique (CLAIMED) ; aucun volume cible n'est fixé par Google.
5. **Maillage** : un hub par thème (page mère) liant ses pages filles en `<a href>` à ancre
   descriptive ; chaque fille renvoie à la mère et à 2-3 sœurs réellement proches (pas à toutes) ;
   le hub est lié depuis l'accueil et le pied de page.
6. **Données structurées** : décrire seulement ce qui est visible ; `BreadcrumbList` pour le
   fil d'Ariane ; `ItemList` ne donne de carrousel que pour quatre types (cours, film, recette,
   restaurant) ; `LocalBusiness` seulement sur la page de l'entité qu'elle décrit.
7. **Suivre** : relever à date fixe les mêmes requêtes (SERP et Search Console) et consigner
   dans un journal ; une page sans impression après 8 semaines est réécrite ou retirée.

## Compléments de praticiens (2026-11-08, tous CLAIMED)
Source : Paul Vengeons (article X du 2026-10-21, note X du 2026-11-07) et Laurent Bourrelly (blog), lus le
2026-11-08, détail et numéros V/B-N dans [french-practitioners.md](french-practitioners.md). Aucune donnée
publiée : ce sont des **tests manuels et des repères**, jamais des P0 ou P1.
1. **Un motif = une intention, un type de page** (V3) : « X vs Y », « alternative à X », « service + ville ».
   Plusieurs variantes seulement si chaque page apporte une donnée propre (règle 2 ci-dessus). Les pages
   « service + ville » qui ne diffèrent que par la ville sont des *doorways* (spam policies, maj 2026-08-28).
2. **Test d'ouverture** (V4) : pour chaque requête retenue, noter si au moins un des trois premiers résultats a
   le mot-clé exact dans son title. Aucun : porte ouverte. Ne prouve pas que Google préfère un title ; c'est
   un indice de faible optimisation.
3. **Odeur de la SERP et faisabilité** (B-N2) : avant de produire, noter les types d'URL en tête (marques,
   encyclopédie, forums, vidéos), la présence d'un AI Overview, et si une entité occupe la place de « la
   réponse ». Si oui, la requête est probablement inatteignable pour une page ordinaire : la retirer ou la
   reformuler.
4. **Quick wins** (V5) : pages en positions 5 à 20 dans Search Console. Filtrer sur la page ET la requête
   avant de lire la position moyenne (la moyenne d'un site mélange des requêtes sans rapport).
5. **Bandes d'autorité** (V2, CLAIMED) : site à moins de 20 de DR (Ahrefs) = longue traîne ; 20 à 40 = moyenne
   traîne ; plus de 40 = têtes de requêtes ; moins de 50 domaines référents = peu de requêtes compétitives
   accessibles. Le DR n'est pas un signal Google : ne s'en servir que pour choisir des cibles. **Divergence** :
   Bourrelly juge la longue traîne perdante ; l'arbitrage dépend de l'autorité réelle du site.
6. **Anatomie du title** (V7) : mot-clé exact au début, une promesse vérifiable, l'année seulement si le
   contenu est à jour, « best » seulement si un classement fondé suit, environ 600 px. Google réécrit les
   titres qu'il juge trompeurs ([title links](https://developers.google.com/search/docs/appearance/title-link)).
7. **Registre des modifications** (V12) : consigner pour chaque page la date, la modification et la mesure de
   départ ; ne pas rejuger avant la fin des délais (repères Google : [exact-match-domains.md](exact-match-domains.md)).
   La « règle des 90 jours » de Vengeons est une pratique, non un délai Google.
8. **Cadence** (V11) : site neuf, environ 1 page par semaine ; site établi, jusqu'à 2 par semaine ; jamais plus
   d'une page par jour. Repère de prudence face au *scaled content abuse*, pas un plafond Google ; le contrôle
   `publication-burst` de l'audit reste la mesure.
9. **Ne pas traduire les mots-clés marché par marché** (V14) : un seul domaine, un répertoire par langue.

## Ce qu'il faut éviter (consignes Google)
| Règle | Niveau | Source (date) |
|---|---|---|
| *Scaled content abuse* : produire beaucoup de pages d'abord pour classer, sans valeur pour le lecteur, quel que soit le moyen (IA, humain ou mélange) | ESTABLISHED | [blog Google](https://developers.google.com/search/blog/2024/03/core-update-spam-policies) (2024-03-05) ; [spam policies](https://developers.google.com/search/docs/essentials/spam-policies) (consultée le 2026-11-03, date de mise à jour non affichée) |
| *Doorway abuse* : pages visant des requêtes proches ou des villes qui mènent toutes vers la même destination, pages quasi identiques placées avant une structure navigable | ESTABLISHED | spam policies, même page (2026-11-03) |
| Ne pas créer une page par variante de requête ou par sous-question dans l'espoir de classer ; ajouter des pages n'élève pas la qualité du site | ESTABLISHED | [guide d'optimisation IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (consulté le 2026-11-03 ; maj 2026-07-10 selon la référence du skill) |
| L'automatisation n'est pas interdite en soi : le critère est la valeur et l'intention ; l'usage d'automatisation ou d'IA pour manipuler le classement est du spam | ESTABLISHED | [blog Google](https://developers.google.com/search/blog/2023/02/google-search-and-ai-content) (2023-02-08) |
| Signaux d'un contenu fait pour les moteurs : sujets publiés au hasard, automatisation lourde, résumé des autres sans apport, dates changées sans mise à jour | ESTABLISHED | [contenu utile](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) (consultée le 2026-11-03, date non affichée) |
| `noindex` retire la page des résultats ; la page ne doit pas être bloquée par robots.txt, sinon la directive n'est pas lue | ESTABLISHED | [bloquer l'indexation](https://developers.google.com/search/docs/crawling-indexing/block-indexing) (consultée le 2026-11-03) |
| Carrousels : `ItemList` éligible seulement avec cours, film, recette ou restaurant ; une galerie générique n'a pas de rich result | ESTABLISHED | [carrousel](https://developers.google.com/search/docs/appearance/structured-data/carousel) (consultée le 2026-11-03) |

Autres interdits de la méthode : bourrer les titres de variantes, fabriquer des « études » ou
chiffres sans source, afficher des avis ou notes que le site ne détient pas, reprendre le
plan d'un concurrent, publier sans relecture humaine ([automation.md](automation.md)).

## Sortie attendue
Un fichier daté `keywords_<AAAAMMJJ>.md` : tableau de notation, matrice brute en annexe, SERP
lues (requête, date, moteur, résultats), plan de pages avec la preuve exigée par page, et une
liste **« inconnu »** (Trends inaccessible, volumes, ordre réel sur Google).
