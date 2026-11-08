# Domaines à correspondance exacte, réseaux de sites et stratégies « achat de domaines puis attente »

Revu le 2026-11-08. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
Pages Google lues le 2026-11-08 : [spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
(« Last updated 2026-08-28 UTC »), [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
(« Last updated 2025-12-10 UTC »), [journal des mises à jour](https://developers.google.com/search/updates) (« Last updated 2026-10-26 UTC »).

À utiliser quand on propose, ou qu'on évalue, l'achat de noms de domaine contenant le mot-clé visé
(« best-data-labs », « best-data-labelling-tools »…), la création de plusieurs sites par requête, ou une
promesse de classement rapide fondée sur le nom de domaine. **Décision d'achat de domaine : au propriétaire,
jamais tranchée par le skill** (dépense, voir SKILL.md).

## Ce que Google dit (ESTABLISHED)

| Affirmation | Source (date) |
|---|---|
| Les mots-clés du nom de domaine ou du chemin d'URL « have hardly any effect beyond appearing in breadcrumbs ». Le TLD ne compte que pour cibler un pays, et même alors faiblement | [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) (maj 2025-12-10, lu 2026-11-08) |
| Mise à jour « EMD » : Matt Cutts annonce que Google réduit le classement des domaines à correspondance exacte **de basse qualité** (0,6 % des requêtes en anglais aux États-Unis). Un domaine à mot-clé de qualité n'était pas visé. Tweet de Cutts non relu à la source, relayé par Sistrix (27 septembre 2012) et Search Engine Roundtable | [Sistrix](https://www.sistrix.com/?p=32116) ; [SER](https://seroundtable.com/google-emd-update-15776.html) (2012-09-27/28) |
| John Mueller (Google) : « In short, you don't need to put keywords in the domain name » (2020), puis « I'm not a fan of keyword-keyword domains, but YMMV » (commentaire Reddit r/SEO, relayé le 2023-02-15). Déclarations d'un employé Google, relayées, vidéo et fil non relus | [SEJ, 2020-09-15](https://www.searchenginejournal.com/keywords-in-domain-name/380912/) ; [SEJ, 2023-02-15](https://www.searchenginejournal.com/googles-john-mueller-cautions-against-keyword-rich-domains/479777/) |
| *Doorway abuse* : « Having multiple websites with slight variations to the URL and home page to maximize their reach for any specific query » ; « multiple domain names or pages targeted at specific regions or cities that funnel users to one page » | [spam policies](https://developers.google.com/search/docs/essentials/spam-policies) (maj 2026-08-28) |
| *Scaled content abuse* : beaucoup de pages produites surtout pour manipuler le classement, quel que soit le moyen ; inclut « Creating multiple sites with the intent of hiding the scaled nature of the content » | idem |
| *Expired domain abuse* : domaine expiré racheté et réutilisé surtout pour manipuler le classement avec un contenu sans valeur (exemples : affiliation sur un ancien site d'administration, casino sur un ancien site d'école) | idem |
| *Link spam* : achat ou vente de liens pour le classement ; « Excessive link exchanges » et pages de partenaires « exclusively for the sake of cross-linking » | idem |
| Le désaveu est « advanced » ; « most sites will not need to use this tool » | [Disavow links](https://support.google.com/webmasters/answer/2648487) (page sans date affichée, lue le 2026-11-08) |
| Mises à jour récentes : cœur de mai 2026 (terminée le 2026-06-02), spam updates de juin, août et septembre 2026. La spam update de septembre a couru du 2026-09-24 au 2026-10-08 selon des relevés tiers (tableau de bord Google non relu). Aucune mise à jour confirmée en octobre ni début novembre au 2026-11-06 (relevés tiers) | [Search Status Dashboard](https://status.search.google.com/) via relevés tiers, 2026-11-06 |
| Délais indicatifs donnés par un employé Google (Gary Illyes, Search Central Live Barcelone, 2026-10-02) : nouvelle URL découverte en ~20 h, titre modifié en 1-2 jours, canonical en 1-3 semaines, récupération après mise à jour du cœur en 3-6 mois. Ce sont des repères, pas des délais ; diapositives non publiées, recap d'un tiers relayé par SEJ | [SEJ, 2026-10-04](https://www.searchenginejournal.com/google-crawling-indexing-recovery-timing-ranges/591829/) (CLAIMED tant que la source n'est pas relue) |

## Ce que la stratégie « domaines exacts, proximité lexicale, entités, 10 jours » contient, ligne par ligne

Stratégie telle que décrite par le propriétaire (lue sur X : « rank number 1 on Google + LLMs, 0 to 7 figures in
10 days », domaines du type « best data labs »). Le texte d'origine n'a **pas** été retrouvé le 2026-11-08 : il
n'est dans aucune des deux publications du jour (alg0_slayer, VengeonsP) et trois recherches web n'ont rien
donné. Les lignes ci-dessous évaluent donc les éléments décrits, pas une source.

| Élément | Verdict | Étiquette et source |
|---|---|---|
| Domaine à correspondance exacte pour un gain de classement | Gain non documenté : Google dit que le mot-clé du domaine n'a presque aucun effet. Un domaine à mot-clé *de basse qualité* a été visé dès 2012 | ESTABLISHED (SEO Starter Guide ; EMD 2012) |
| Un domaine par requête (« best X », « best Y »…) renvoyant vers une offre | Correspond à la définition de *doorway abuse* si les sites sont des variantes qui poussent vers une destination unique, et à *scaled content abuse* si l'ensemble masque une production de masse | ESTABLISHED (spam policies) |
| Contenu à forte proximité lexicale entre pages | Pages quasi identiques sur des requêtes voisines : *doorways*. Le contrôle du skill (`hygiene_check.py content`, seuil de recoupement 60 %) le mesure | ESTABLISHED (principe) ; seuil CLAIMED (skill) |
| Cartographie d'entités | Pratique éditoriale légitime (carte de la demande, définition canonique) quand elle sert un site avec un but principal. Elle n'a **aucun effet démontré** sur un classement en dix jours | CLAIMED ([french-practitioners.md](french-practitioners.md), B1, B8, D2) |
| Domaines expirés rachetés pour leur autorité | *Expired domain abuse* si le contenu n'a pas de rapport avec l'usage d'origine | ESTABLISHED |
| Se classer n°1 sur Google et dans les LLM en dix jours | Possible sur une requête que personne ne vise (long tail sans concurrent) ; ni documenté, ni reproductible sur une requête commerciale. Délais de Google : voir le tableau ci-dessus | CLAIMED (aucune donnée publiée) |
| « 7 chiffres » (chiffre d'affaires) | Aucune preuve vérifiable dans les sources lues. À traiter comme une promesse commerciale | CLAIMED |
| Citation par les LLM grâce à la position Google | Recouvrement partiel et variable : voir [evidence.md](evidence.md) (AI Overviews ~38 %, ChatGPT ~10 % de recouvrement avec le top 10 selon Ahrefs) | CLAIMED, méthode publiée |

**Ce que fait le skill face à une telle demande** : ne pas recommander l'achat de domaines à mot-clé exact ni
la multiplication de sites par requête ; proposer à la place une page par intention sur le domaine de marque
([keyword-research.md](keyword-research.md)), avec une preuve propre par page. Si le propriétaire décide
malgré tout d'acheter un domaine, lui dire par écrit les risques ci-dessus, vérifier l'historique du domaine
(*expired domain abuse*), et ne jamais faire se lier ses sites entre eux sans raison éditoriale réelle
([backlinks.md](backlinks.md), section PBN).

## Contrôles à lancer

1. Domaine candidat : historique (Archive.org, Search Console du domaine s'il est déjà vérifié), thème
   d'origine compatible avec le futur contenu ; sinon écarter.
2. Plusieurs sites du même propriétaire : chacun a son public, son contenu propre, aucun lien croisé sans
   raison éditoriale ; pas de gabarit et de texte copiés d'un site à l'autre
   ([helpful-content-small-site.md](helpful-content-small-site.md), « Limites »).
3. Avant publication d'un lot : `hygiene_check.py content --site <url>` (`near-duplicate-pages`,
   `publication-burst`) ; un recoupement élevé = fusionner, `noindex`, ou réécrire avec une preuve propre.
4. Après publication : Search Console, rapport Performances filtré sur la page, relevé à date fixe. Ne pas
   conclure avant la fin des délais de Google (voir plus haut) ; un classement obtenu en dix jours sur une
   requête sans concurrent ne prouve rien sur la tenue à 3-6 mois.
