# Contenu utile : contrôles pour un petit site sans clients ni trafic

Revu le 2026-11-04 (v2.7.0). Sources officielles lues le 2026-11-04 :
- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content),
  **« Last updated 2026-10-05 UTC »** (ESTABLISHED) ;
- [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies), maj 2026-08-28 ;
- [Contenu généré par IA](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content), maj 2026-10-01.

## Vérification de la date du 2026-10-05
La date est **exacte** : la page affiche « Last updated 2026-10-05 UTC ». La version précédente
(instantané Internet Archive du 2026-09-21) portait « Last updated 2025-12-10 UTC ». Nuance :
le journal des mises à jour de Search Central n'a **aucune entrée datée du 5 octobre 2026** (entrées
d'octobre relues : 1, 8, 16, 21, 23 et 26) ; la modification n'a donc pas été annoncée. Écart entre les
deux versions (comparaison de texte du 2026-11-04) :
- **ajout** d'une section « Main content » : la qualité du contenu principal est décrite par quatre
  attributs, **Effort** (travail humain réel ; « generating pages from feeds or using generative AI to
  produce large amounts of text without manual oversight or curation represents little to no
  effort » ; citer ses sources « doesn't replace the need for original effort »), **Originality**,
  **Talent or skill**, **Accuracy** (exigence renforcée pour les sujets YMYL) ; elle renvoie aux
  Search Quality Evaluator Guidelines ;
- le paragraphe sur les **faux profils d'auteur** (têtes générées par IA, noms inventés, fausses
  qualifications = tromperie, signal de page de basse qualité) figure dans la version actuelle ;
  présent ou seulement reformulé dans l'ancienne, non tranché ;
- le reste (questions d'auto-évaluation, Who / How / Why) est inchangé.

## Ce que Google dit, et ne dit pas (ESTABLISHED)
- Le système de contenu utile n'est plus un système séparé : il est intégré aux systèmes de classement
  principaux (journal Search Central, entrée du 2024-08-15).
- **Rien dans ces pages ne pénalise un site parce qu'il est neuf ou sans trafic.** Le risque vient des
  motifs : contenu produit surtout pour les moteurs, de masse, mince ou doublé.
- Pas de nombre de mots préféré (« No, we don't »), pas de fréquence de publication prescrite.
- Ajouter ou retirer beaucoup de contenu « pour paraître frais » ne sert à rien, et changer la date d'une
  page dont le contenu n'a pas changé est un signal d'alerte.

## Contrôles de l'audit

Commande : `python scripts/hygiene_check.py content --site <url>` (lit le sitemap, échantillonne les
pages, liste ; le propriétaire décide). Les seuils du script sont ceux du skill, pas ceux de Google.

| # | Contrôle | Vérification | Étiquette, source |
|---|---|---|---|
| H1 | **Pensé pour les acheteurs** : chaque page répond à une question d'un acheteur précis (public existant ou visé), le site a un but principal, et le lecteur repart avec de quoi agir | Revue : une page = une intention de la carte de la demande ([content-formats.md](content-formats.md)) ; page sans acheteur identifiable = à fusionner ou retirer | ESTABLISHED : « Do you have an existing or intended audience... », « Does your site have a primary purpose or focus? », « After reading your content, will someone leave feeling they've learned enough... » |
| H2 | **Pas de contenu de masse** : aucune série de pages créée surtout pour classer, aucune page par variante de requête | `hygiene_check.py content` (`near-duplicate-pages`, `publication-burst`) ; compter les pages créées par semaine | ESTABLISHED, scaled content abuse : « many pages are generated for the primary purpose of manipulating search rankings... no matter how it's created », y compris l'IA générative sans valeur ajoutée. Google range aussi dans cette catégorie la page par requête « fan-out » ([spam-policies.md](spam-policies.md)) |
| H3 | **Preuve de première main** : exemples réels, mesures, captures, essais menés par le site, chiffres datés. Sans client : démos, tests du propre produit, données propres, jamais d'avis, de cas client ou de chiffre inventés | Revue : chaque page de fond contient au moins un élément que seul le site peut apporter | ESTABLISHED : « first-hand expertise... having actually used a product or service » ; Effort et Originality (section « Main content » du 2026-10-05). Interdire l'invention : voir [schema-templates.md](schema-templates.md) |
| H4 | **Auteur visible** : signature sur chaque page de fond, lien vers une page auteur et une page À-propos réelles | `hygiene_check.py content` (`no-byline`) ; contrôle de l'unicité du profil dans le JSON-LD (`author.url`, [eeat-news.md](eeat-news.md)) | ESTABLISHED : « Do pages carry a byline, where one might be expected? », « Do bylines lead to further information about the author? ». Profil inventé (photo générée, faux nom, fausses qualifications) = tromperie |
| H5 | **Expérience affichée** : l'auteur dit ce qu'il a fait ou testé, et comment | Revue : méthode et durée du test, matériel, limites | ESTABLISHED (section « How », avis produits : nombre de produits testés, résultats, méthode, photos) |
| H6 | **Fréquence raisonnable** : un rythme que la relecture humaine suit ; pas de lot de dizaines de pages le même jour ; date modifiée seulement après un vrai changement de fond | `publication-burst` ; revue de l'historique git du site | Le principe est ESTABLISHED (pas de « fraîcheur » artificielle, pas de date changée sans changement). **Un nombre de pages par semaine est CLAIMED** : Google n'en donne aucun, ne pas le présenter comme une règle |
| H7 | **Pages ville et métier qui ne sont pas des doublons** | `near-duplicate-pages` : pages sœurs sous un même motif d'URL, dont le texte propre (hors menu et pied de page) se recoupe à 60 % ou plus (seuil du skill) | ESTABLISHED, doorway abuse : « multiple domain names or pages targeted at specific regions or cities that funnel users to one page », « substantially similar pages that are closer to search results than a clearly defined, browseable hierarchy ». Règle d'application (SUPPORTED, déduction) : une page par ville seulement si elle porte du contenu propre (intervention réelle, prix constatés, zone, photos, cas) ; sinon une page « zones » unique ; sinon `noindex` |
| H8 | **Contenu assisté par IA** : relu et corrigé par un humain, méthode indiquée quand elle compte, aucune page produite en lot sans supervision | Revue ; chaîne de relecture du projet | ESTABLISHED : section « How » ; page IA de Google (maj 2026-10-01) ; « Are you using extensive automation to produce content on many topics? » est un signal d'alerte |
| H9 | **Sujets hors de l'expertise réelle** : aucune page sur un thème choisi uniquement pour son trafic ; exactitude renforcée si le sujet touche la santé, l'argent ou la sécurité (YMYL) | Revue éditoriale | ESTABLISHED : « Did you decide to enter some niche topic area without any real expertise... », Accuracy (YMYL) |
| H10 | **Pages minces** : une page de moins de 150 mots est relue, pas gonflée | `thin-pages` (P2) | CLAIMED : le seuil est celui du skill ; Google n'a pas de nombre de mots préféré. Rejoint le contrôle « soft 404 » déjà dans l'audit |
| H11 | **Pas de signal d'alerte éditorial** : titres non exagérés, pas d'annonce d'une réponse qui n'existe pas, pas de réécriture de sources sans apport | Revue | ESTABLISHED (questions « Content and quality » et « Avoid creating search engine-first content ») |

## Priorités pour un petit site (ordre)
1. H2 et H7 : ce sont les motifs que les politiques anti-spam nomment, donc le vrai risque de pénalité.
2. H3 et H4 : ce que les systèmes de classement et les évaluateurs cherchent en premier, et ce qu'un site sans
   clients peut produire seul.
3. H6, H1, H8, H9, puis H10 et H11.

## Repères de cadence (ajout du 2026-11-08, CLAIMED)
Paul Vengeons (article X du 2026-10-21) recommande, pour un site neuf, environ 1 page par semaine (jusqu'à 2 par
semaine sur un site établi), jamais plus d'une par jour, chaque page avec un brief distinct, et réserve le
programmatic SEO aux sites déjà autoritaires. Aucune donnée publiée, et son billet du 2026-04-22 conseillait
une page par jour : à utiliser comme prudence en face de H6 et du contrôle `publication-burst`, pas comme seuil.
Il dit lui-même que ses pages « service + ville » ont perdu des impressions après 3 à 4 ans (voir H2 et H7).

## Limites
- Le script ne juge pas la qualité : il mesure des indices (recoupement de texte, présence d'une
  signature, dates). Un faux positif est possible (pages courtes légitimes, fiches techniques
  proches par nature) ; un faux négatif aussi (pages différentes mais vides de substance).
- Une pénalité manuelle se voit dans Search Console (Actions manuelles) ; une baisse algorithmique ne
  s'y annonce pas. Sans accès Search Console, le dire, ne pas extrapoler.
- Les trois sites d'un même propriétaire qui partagent un gabarit ou un texte (pied de page, À-propos,
  paragraphes réutilisés) ne sont pas un « réseau de sites » au sens de la politique tant que chacun
  répond à son propre public ; rester prudent sur tout texte copié d'un site à l'autre (SUPPORTED, lecture
  de « spread across a large network of sites », non éprouvée).
