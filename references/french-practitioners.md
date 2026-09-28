# Praticiens SEO français : Laurent Bourrelly et Stéphane Delgado

Revu le 2026-09-28 (posts X lus le 2026-09-28). Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Ce fichier reprend les méthodes publiques de deux praticiens suivis par le
propriétaire du skill. Il dit ce qui est vérifiable et ce qui ne l'est pas, et
comment le skill s'en sert.

**Règle d'arbitrage.** Une méthode de praticien est **CLAIMED** tant qu'elle ne
s'appuie pas sur des données publiées. Elle ne fonde jamais seule une priorité
P0 ou P1 (contrôle automatique : `tests/test_automation.py`). En cas de
conflit avec la documentation primaire de Google, **suivre Google**.

## Laurent Bourrelly — cocon sémantique

Consultant français, auteur du concept de « cocon sémantique ». Son site
[laurentbourrelly.com](https://www.laurentbourrelly.com/) se présente en
2026 comme un cabinet de conseil en « IA souveraine ». Ses articles sur le
cocon restent en ligne sous `/blog/`. Son compte X actif est
[`@aibloodmoon`](https://x.com/aibloodmoon) (l'ancien `@laurentbourelly`
est suspendu) : voir la lecture de ses posts plus bas.

**Ce qui est public et ce qui ne l'est pas.** Ses pages publiques décrivent
des principes. Les règles opératoires sont réservées à sa formation payante :
types de liens, emplacements, ancres, nombre de liens. Sa page de formation
indique qu'elle n'est plus en vente et renvoie vers un atelier payant (lu le
2026-09-28). Le schéma souvent cité est le suivant :
- la mère lie ses filles ;
- chaque fille lie sa mère ;
- les sœurs se lient entre elles ;
- les liens sont placés dans le texte uniquement.

Ce schéma circule chez des tiers. Il n'a pas été trouvé écrit de sa main dans
une page publique. Le skill l'attribue donc à « l'interprétation courante »,
pas à Bourrelly.

| # | Méthode (paraphrase) | Source (date) | Étiquette | Rapport à Google |
|---|---|---|---|---|
| B1 | Le cocon aligne l'offre du site sur la demande des visiteurs. Ce n'est pas qu'une technique de maillage : chaque page a un rôle distinct. | [blog/55718](https://www.laurentbourrelly.com/blog/55718.php) (2024-04-17) ; [blog/54753](https://www.laurentbourrelly.com/blog/54753.php) (2019-03-26) | CLAIMED | Compatible |
| B2 | La recherche de mots-clés part du visiteur, de ses motivations et de ses intentions (persona, carte mentale « en mode demande »), avant de passer à l'offre. | [blog/54247](https://www.laurentbourrelly.com/blog/54247.php) (2015) ; [blog/54940](https://www.laurentbourrelly.com/blog/54940.php) (« version 2020 ») | CLAIMED | Compatible (contenu utile, centré sur l'utilisateur) |
| B3 | Le siloing sert à ranger des données et des produits. Le cocon sert à donner au moteur ce qu'il attend. Les deux sont distincts. | [blog/54748](https://www.laurentbourrelly.com/blog/54748.php) (2019-03-25) | CLAIMED | Compatible |
| B4 | Il parle de PageRank thématique et de « glissement sémantique ». Il cite TF-IDF, le cosinus de Salton et LSA/LDA, tout en reconnaissant ne pas savoir si Google s'en sert. | [blog/1631](https://www.laurentbourrelly.com/blog/1631.php) (non daté) | CLAIMED, sans mesure | Aucune doc Google ne le confirme |
| B5 | Trois types de pages. Les silos sont isolés les uns des autres, avec des passerelles choisies. Il décrit plusieurs typologies de liens placés à différents endroits du code, dont un « super menu ». | [formation cocon](https://www.laurentbourrelly.com/formations/cocon-semantique/) (contenu 2018) | CLAIMED | Compatible. **Contredit** l'idée tierce « liens dans le texte uniquement ». |
| B6 | Le champ lexical prime sur la densité de mots-clés. | [blog/54357](https://www.laurentbourrelly.com/blog/54357.php) (~2015) | CLAIMED | Aligné sur l'interdiction du bourrage de mots-clés |
| B7 | Décliner un sujet en 20 à 30 contenus multimédias. Construire un « cocon off-site », qu'il appelle lui-même un PBN. | [blog/54940](https://www.laurentbourrelly.com/blog/54940.php) (« version 2020 ») | CLAIMED | **Conflit** : un réseau de sites monté pour le classement relève du *link spam*. Une déclinaison à grande échelle sans valeur propre relève du *scaled content abuse* ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies), maj 2026-08-28). **Ne jamais recommander.** |

Aucune affirmation de sa part sur le « Reasonable Surfer » n'a été trouvée
dans les pages lues. Les outils souvent associés au cocon n'ont pas été
développés par lui :
- Cocon.Se : Sylvain Deauré et Christian Moussel ;
- Bombyx4Wp : Benoit Chevillot, sur ses préconisations.

Ces deux attributions viennent d'extraits de recherche, non vérifiés à la
source.

## Stéphane Delgado — GEO et maillage

Identité vérifiée sur ses propres pages le 2026-09-28. Consultant SEO et GEO
indépendant, basé à Bordeaux, qui revendique plus de 25 ans d'expérience.
Il tient [stephanedelgado.fr](https://www.stephanedelgado.fr/consultant-digital/)
et a créé BotSEO, une suite d'agents IA. Il est l'auteur du livre
*Passeport vers la Citation*. Son site est aussi un support commercial,
avec de nombreuses pages « consultant SEO + ville ».

| # | Méthode (paraphrase) | Source (date) | Étiquette | Rapport à Google |
|---|---|---|---|---|
| D1 | Lister 20 à 50 questions réalistes de clients (notoriété, recommandation, comparaison, local). Les poser à ChatGPT, Perplexity et Gemini pour établir une ligne de base : cité ou non, concurrents cités, fidélité de la description. | [comment-etre-cite-par-les-ia](https://www.stephanedelgado.fr/comment-etre-cite-par-les-ia/) (maj 2026-09-03) | CLAIMED | Compatible |
| D2 | Écrire une « définition canonique » de 1 à 3 phrases factuelles, reprise à l'identique sur le site, Google Business Profile, LinkedIn et les annuaires. | idem | CLAIMED | Compatible. Le balisage doit refléter le contenu visible. |
| D3 | Règle des trois sources : chaque fait important doit être confirmé par au moins trois sources externes (presse, avis, podcasts, données). | idem | CLAIMED | Compatible, **si** ces mentions ne sont ni achetées ni fabriquées (*link spam*) |
| D4 | Mesurer chaque mois, sur 10 à 20 requêtes : taux de citation, part de voix, fidélité, sentiment. | idem | CLAIMED ; cas client « 13 % → 67 % » sans protocole | Compatible |
| D5 | Autoriser OAI-SearchBot. Pages indexables, rapides, lisibles sans JavaScript. | idem | ESTABLISHED pour OAI-SearchBot ([OpenAI](https://developers.openai.com/api/docs/bots)) | Compatible |
| D6 | Répondre dans les 150 premiers mots, avec listes, tableaux, définitions, sources datées et auteur identifié. | idem | CLAIMED ; le seuil de 150 mots est arbitraire | Google n'impose aucun format ([AI features](https://developers.google.com/search/docs/appearance/ai-features), maj 2025-12-10) |
| D7 | AI Mode : couvrir les sous-questions (*query fan-out*) avec des passages autonomes, et indiquer des dates de mise à jour honnêtes. | [google-ai-mode](https://www.stephanedelgado.fr/google-ai-mode/) (maj 2026-07-22) | Le fan-out est ESTABLISHED (Google) ; le reste est CLAIMED | Google : ne pas créer une page par sous-requête (*scaled content abuse*) |
| D8 | « 17 à 38 % » des sources citées par les IA seraient aussi en tête de Google. | comment-etre-cite-par-les-ia | **Non sourcé** sur la page. L'ordre de grandeur rejoint Ahrefs (CLAIMED, voir [evidence.md](evidence.md)). | Ne pas reprendre ce chiffre |
| D9 | Maillage : 10 à 15 liens depuis l'accueil, 3 à 10 liens contextuels par article, 3 à 5 liens vers des pages sœurs. Pas de page orpheline, profondeur de 3 clics au plus, ancres descriptives. Le *PageRank sculpting* par nofollow est inefficace. Il écrit lui-même qu'« il n'y a pas de seuil officiel ». | [maillage-interne-seo](https://www.stephanedelgado.fr/maillage-interne-seo/) (non daté) | CLAIMED | Aligné pour les ancres et les orphelines. Google ne fixe **aucun** nombre de liens ([links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable), maj 2025-12-10). |

## Ce que Google dit (référence d'arbitrage, ESTABLISHED)

Toutes les pages ci-dessous ont été lues le 2026-09-28.

- **[Link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)**
  (maj 2025-12-10) :
  - un lien est un `<a href>` ;
  - chaque page importante reçoit un lien d'au moins une autre page du site ;
  - l'ancre est descriptive et concise, pas « click here » ni « read more » ;
  - il n'y a pas de nombre idéal de liens : « if you think it's too much,
    then it probably is ».
- **[SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)**
  (maj 2025-12-10) : ancres descriptives, regroupement des pages par
  répertoire, pas de nombre de mots magique.
- **[Spam policies](https://developers.google.com/search/docs/essentials/spam-policies)**
  (maj 2026-08-28) : bourrage de mots-clés, *scaled content abuse*, *link
  spam* et *doorways*. Les *doorways* sont des pages similaires plutôt qu'une
  hiérarchie navigable.
- **[Breadcrumb](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)**
  (maj 2026-09-08) : le fil d'Ariane indique la position de la page dans la
  hiérarchie du site.

## Ce qui entre dans le skill

### Contrôles automatiques (`scripts/linkgraph.py`, lancés par `scripts/run_audit.py`)

| Contrôle | Code de constat | Étiquette | Seuil |
|---|---|---|---|
| Page du sitemap sans lien interne entrant (orpheline) | `orphan-page` (P1) | ESTABLISHED (Google) | ≥ 1 lien : sourcé |
| `<a>` sans `href` ou en `javascript:` | `non-crawlable-link` | ESTABLISHED | — |
| Ancre générique ou vide | `generic-anchor`, `empty-anchor` | ESTABLISHED | liste FR/EN dans `linkgraph.GENERIC_ANCHORS` |
| Lien interne cassé ou vers une redirection | `broken-internal-link`, `link-to-redirect` | ESTABLISHED | — |
| Profondeur de clic > 3 depuis l'accueil | `deep-page` | CLAIMED (D9, convention) | `--max-depth`, arbitraire |
| Page liée seulement par la navigation | `no-contextual-inlink` | CLAIMED (B5, D9) | 0 lien dans `<main>`/`<article>` |
| Page sans lien contextuel sortant | `no-contextual-outlink` | CLAIMED (D9) | 0 ; la fourchette 3-10 de D9 n'est **pas** reprise |
| Fille sans lien vers sa page mère (par répertoire) | `cocoon-no-uplink` | CLAIMED (interprétation courante) | — |
| Même ancre exacte pour ≥ 80 % de ≥ 5 liens contextuels | `anchor-repeated` | CLAIMED (B5, B6) | arbitraire |
| Tableau des rubriques : mère, filles, liens montants et descendants, liens entre sœurs, part des liens qui sortent de la rubrique | — (rapport) | CLAIMED (B5) | aucun seuil : lecture humaine |

Un lien est dit **contextuel** quand il est placé dans `<main>` ou
`<article>`, hors de `<nav>` et `<aside>`. Si le site ne balise pas ces zones,
les contrôles contextuels sont désactivés et le rapport le dit.

La rubrique est déduite du répertoire de l'URL (`/fr/robots/x` appartient à
`/fr/robots`). C'est une approximation : un cocon peut ne pas suivre les
répertoires. Dans ce cas, le tableau se lit comme un indice, pas comme un
verdict.

### Étapes manuelles (ajoutées à la procédure, pas automatisables sans API payante)

1. **Carte de la demande** (B2) : avant de créer des pages, lister les
   intentions des visiteurs et les regrouper par sujet. Une page par
   intention, jamais une page par variante de requête.
2. **Ligne de base des citations IA** (D1, D4) : poser à la main 10 à 20
   questions réelles aux assistants et noter la date, la source citée et la
   fidélité de la description. Ce relevé est **mesuré, mais manuel**, et
   n'est pas reproductible à l'identique : les réponses varient.
   Côté Google et Bing, préférer les rapports « Generative AI performance » et
   « AI Performance » ([google-ai-features.md](google-ai-features.md)).
3. **Définition canonique** (D2) : vérifier que le nom et la description de
   l'entité sont identiques sur le site (JSON-LD `Organization`, page
   À propos) et sur les profils externes.
4. **Lecture de la SERP** (BX2) : avant d'écrire une page, noter ce que
   Google montre pour la requête visée (types de pages, formats, angles).
   La page produite doit répondre à cette intention, pas la copier.

## Ce qui n'entre pas

- Le PBN ou « cocon off-site » (B7), le « réseau de liens privé » (BX6),
  l'achat d'un lien « pour tester » (BX5) et toute mention achetée ou
  fabriquée (limite de D3) : *link spam*.
- La déclinaison d'un sujet en dizaines de pages sans valeur propre (B7) :
  *scaled content abuse*.
- Les seuils présentés comme des règles : 150 mots (D6), nombre de liens par
  page (D9). Ils restent des paramètres, jamais des exigences.
- Les statistiques sans source (D8).

## Posts X : lecture du 2026-09-28

Lecture faite avec l'outil de lecture du propriétaire, sur ses propres
comptes utilisateur X (pas l'API X), au rythme de l'outil : une requête à la
fois, 10 s au moins entre deux requêtes. Les posts de `@aibloodmoon` ont été
lus le même jour, après réparation de l'outil (bibliothèque Scweet 5.8.0). Posts publics seulement, au plus
les 100 derniers posts originaux par compte (ni retweet, ni réponse à un
tiers). La tentative précédente par l'API X avait échoué (401, aucun post
lu).

| Personne | Compte | Constat du 2026-09-28 | Posts lus |
|---|---|---|---|
| Laurent Bourrelly | `@laurentbourelly` (un seul « r »), lié depuis [contact.php](https://www.laurentbourrelly.com/contact.php) | X répond « User is suspended » (`UserUnavailable`, raison `Suspended`). La variante `@laurentbourrelly` (deux « r ») ne renvoie aucun compte. | **0** : compte suspendu |
| Laurent Bourrelly | [`@aibloodmoon`](https://x.com/aibloodmoon), compte actif signalé par le propriétaire du skill | Nom affiché « Laurent Bourrelly », compte créé en 2018, lien de bio vers `aibloodmoon.com`. **Identité confirmée** par ses posts : liens vers laurentbourrelly.com ([2101670733050937414](https://x.com/aibloodmoon/status/2101670733050937414), [2098068083789168836](https://x.com/aibloodmoon/status/2098068083789168836)), revendication du cocon sémantique, et mention de son ancien compte banni qu'il n'a pas cherché à récupérer ([2098389504021180570](https://x.com/aibloodmoon/status/2098389504021180570), 2026-09-11). | 160 posts renvoyés par la timeline publique (sans les réponses) : 23 retweets, 137 originaux. **Les 100 plus récents sont lus** (du 2026-09-01 au 2026-09-28). |
| Stéphane Delgado | `@stephdelgado`, lié depuis le pied de page de [stephanedelgado.fr](https://www.stephanedelgado.fr/) | Compte inactif : 2 posts, 3 abonnés, créé en 2014, sans bio | non lu (inactif) |
| Stéphane Delgado | [`@Stephanedelgado`](https://x.com/Stephanedelgado) | **Compte actif retenu.** Bio « Stratège en visibilité IA (SEO/GEO) », fondateur d'un service d'agents IA SEO. Le lien de la bio redirige vers `https://www.stephanedelgado.fr/` (vérifié le 2026-09-28). 65 posts au compteur, réponses comprises. | 10 posts renvoyés par la timeline publique (sans les réponses) : 1 retweet, **9 originaux**. Le plafond de 100 n'est pas atteint. |

Sur les 9 posts originaux de `@Stephanedelgado` (du 2026-07-25 au
2026-09-12) :
- 6 portent sur un outil de cartographie des incendies de juillet 2026. Ils
  ne contiennent aucune méthode SEO/GEO et ne sont pas repris.
- 3 portent sur le SEO/GEO. Chacun accompagne une vidéo, non consultée :
  seul le texte du post est repris.

| # | Post (date) | Méthode (paraphrase) | Étiquette | Rapport à Google et aux fournisseurs |
|---|---|---|---|---|
| X1 | [status/2098747024120164661](https://x.com/Stephanedelgado/status/2098747024120164661) (2026-09-12) | ChatGPT « ignore les backlinks ». Il se poserait trois questions : sait-il qui vous êtes, peut-il reprendre ce que vous dites, d'autres sources le confirment-elles ? | CLAIMED, sans données | Les trois questions reprennent D2 (entité claire), D6 (texte réutilisable) et D3 (confirmation par des tiers). **« Ignore les backlinks » n'est pas vérifiable** : OpenAI ne publie aucun critère de sélection des sources ([evidence.md](evidence.md)). D'après un extrait de recherche (page d'aide OpenAI en 403, **non vérifié**), ChatGPT search s'appuie sur des moteurs de recherche tiers, dont Bing : l'affirmation porte donc sur un système dont on ne connaît pas les critères. Ne pas reprendre comme règle. |
| X2 | [status/2098444001338638429](https://x.com/Stephanedelgado/status/2098444001338638429) (2026-09-11) | « Le GEO, c'est du SEO bien fait. » Le netlinking perd sa place au profit « d'autres piliers », que le post ne nomme pas. | CLAIMED | La première phrase rejoint Google : l'optimisation pour l'IA « reste du SEO » ([guide IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), maj 2026-07-10). La seconde n'est pas étayée. |
| X3 | [status/2098347778401321012](https://x.com/Stephanedelgado/status/2098347778401321012) (2026-09-11) | Annonce d'un entretien vidéo sur le SEO, le GEO et la visibilité dans les IA. | — | Aucune méthode dans le texte : non repris. |

**Ce que X ajoute au skill : rien de nouveau à contrôler.** X1 résume en
une phrase la démarche déjà décrite par D1 à D6. Aucun seuil, aucune donnée
et aucune méthode opératoire n'apparaissent dans les posts. L'affirmation
« ChatGPT ignore les backlinks » reste CLAIMED et n'entre ni dans les
règles ni dans la checklist.

### Laurent Bourrelly (`@aibloodmoon`), 100 posts originaux du 2026-09-01 au 2026-09-28

**14 posts sur 100 portent sur le SEO/GEO.** Parmi eux, 5 ne font que
relancer ou annoncer un live sans méthode. Les autres parlent surtout d'IA
(modèles locaux, critique des laboratoires), de vidéo et de YouTube, de
musique techno et de sa vie personnelle. Beaucoup de
posts annoncent un live vidéo, non consulté : seul le texte du post est
repris, plus l'article du blog vers lequel pointe un post (BX3).

| # | Post (date) | Méthode (paraphrase) | Étiquette | Rapport à Google |
|---|---|---|---|---|
| BX1 | [status/2101990146035843437](https://x.com/aibloodmoon/status/2101990146035843437) (2026-09-21) | Le GEO est surtout une nouvelle étiquette sur un ancien travail. AI Overviews et *query fan-out* changent la distribution du trafic, pas les fondamentaux. La vraie question : pourquoi Google choisirait cette page comme réponse, et pourquoi les pages voisines confirment qu'elle appartient au sujet. | CLAIMED | Compatible : l'optimisation pour l'IA « reste du SEO » ([guide IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), maj 2026-07-10). La confirmation par les pages voisines reprend B1 et B5. |
| BX2 | idem | « Sentir la SERP » avant de produire : regarder ce que Google montre déjà pour la requête, puis écrire. | CLAIMED | Compatible (contenu utile, intention de recherche). Aucune méthode opératoire publiée. |
| BX3 | [status/2101670733050937414](https://x.com/aibloodmoon/status/2101670733050937414) (2026-09-20), qui renvoie vers [blog/59274](https://www.laurentbourrelly.com/blog/59274.php) (non daté, lu le 2026-09-28) | Trois distances : sur la page, rendre le sujet identifiable sans bourrage (le « mot mystère ») ; sur le site, entourer la page de contenus vraiment liés, avec un lien seulement quand la page suivante est le prochain indice du sujet ; hors du site, occuper le même voisinage sémantique (mentions, citations, liens). Ni `llms.txt` obligatoire ni format spécial pour l'IA. | CLAIMED ; l'article ne cite aucune étude | Compatible : Google ne demande aucun fichier ni balisage propre à l'IA ([AI features](https://developers.google.com/search/docs/appearance/ai-features), maj 2025-12-10). Les chiffres d'audience d'AI Overviews de l'article ne sont pas repris ici. |
| BX4 | [status/2098783129116742097](https://x.com/aibloodmoon/status/2098783129116742097) (2026-09-12) | Le cocon n'a jamais été qu'une technique de maillage interne. Il faut construire une marque, un profil de liens sans aucun achat, et un cocon multimédia et omnicanal (vidéo, YouTube, recherche visuelle). | CLAIMED | Compatible pour l'absence d'achat de liens ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies), maj 2026-08-28). **Contredit par BX6.** |
| BX5 | [status/2102740976963908009](https://x.com/aibloodmoon/status/2102740976963908009) (2026-09-23) | Achat de liens : Google ne pénalise pas le site vendeur de liens, il coupe le PageRank de tous ses liens sortants, « depuis plus de 15 ans ». Pour savoir si un lien acheté marche : acheter un seul lien, attendre 3 à 6 mois sans rien changer, observer. Le lien resterait le levier le plus puissant du SEO. Le marché français de la vente de liens dépasserait 10 M€ par an. | CLAIMED ; chiffre de marché sans source | La neutralisation est **confirmée** par Google : SpamBrain détecte les sites qui achètent des liens et ceux qui servent à en passer, et les liens non naturels perdent leur crédit ([link spam update](https://developers.google.com/search/blog/2022/12/december-22-link-spam-update), 2022-12-14). **Conflit** : acheter un lien pour le classement, même « pour tester », relève du *link spam*. Le test à une variable n'est pas reproductible (mises à jour, concurrents). **Ne jamais recommander.** Google ne classe pas publiquement ses facteurs : « le levier le plus puissant » n'est pas vérifiable. |
| BX6 | [status/2095902263197802761](https://x.com/aibloodmoon/status/2095902263197802761) (2026-09-04) | Construire un réseau de liens privé (« Private Links Network ») plutôt qu'un PBN de blogs ; toute entreprise ambitieuse en aurait un. | CLAIMED | **Conflit** : un réseau de sites monté pour passer des liens relève du *link spam* ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies), maj 2026-08-28), et SpamBrain détecte les sites qui passent des liens (BX5). Confirme B7. **Ne jamais recommander.** |
| BX7 | [status/2102050599499952199](https://x.com/aibloodmoon/status/2102050599499952199) (2026-09-21) ; [status/2102792553833902478](https://x.com/aibloodmoon/status/2102792553833902478) (2026-09-23) | Faire indexer des notebooks NotebookLM partagés, c'est du *parasite SEO*, une nouvelle version des réseaux de liens. Le second post relaie Glenn Gabe : Google a retiré l'annuaire des notebooks partagés de ses résultats. | CLAIMED (constat relayé, non vérifié à la source) | Aligné : publier sur le site d'un tiers pour profiter de sa réputation relève du *site reputation abuse* ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies)). |
| BX8 | [status/2096587638207566061](https://x.com/aibloodmoon/status/2096587638207566061) (2026-09-06) | YouTube : l'algorithme regroupe les vidéos en grappes sémantiques tirées de l'historique de visionnage ; le cocon s'y applique. Pas d'impressions = sujet mal ciblé ; ensuite le CTR (titre, miniature) décide. | CLAIMED ; les annonces YouTube évoquées ne sont pas liées | Hors du périmètre de la recherche Google. Rien à contrôler dans le code d'un site. |
| BX9 | [status/2100142497007599866](https://x.com/aibloodmoon/status/2100142497007599866) (2026-09-16) | Relaie un test : coller un extrait de sa page dans ChatGPT et lui demander l'URL correspondante, pour voir s'il la retrouve. Il rappelle que le *New York Times* a procédé ainsi en 2023. | CLAIMED ; test manuel, non reproductible | Compatible avec la ligne de base D1. Ne mesure pas une citation réelle. |

**Ce que ces posts ajoutent au skill.**
- Une étape manuelle : lire la page de résultats avant de produire (BX2,
  étape 4 ci-dessous).
- Une confirmation Google datée (BX5) : les liens non naturels sont
  neutralisés et SpamBrain repère les sites qui en vendent. Cela renforce le
  refus du PBN et de l'achat de liens déjà écrit pour B7.
- Un conflit interne à noter : BX4 prône « 0 achat de lien », BX6 prône un
  réseau de liens privé. Le skill suit Google et écarte BX6.
- Aucun nouveau contrôle automatique : BX1 et BX3 reprennent B1, B2, B5 et
  B6 ; aucun seuil ni aucune donnée n'est publié.

## Sources non lues

- **X (Twitter)** : ancien compte de Bourrelly suspendu ; les 100 derniers
  posts originaux de `@aibloodmoon` sont lus, mais ses lives et vidéos ne
  le sont pas, ni les réponses de ses fils (la timeline publique les
  exclut). Vidéos jointes aux posts de Delgado non consultées.
- LinkedIn et Malt de Stéphane Delgado : mur de connexion, non ouverts.
- Interview de Bourrelly sur `cocon.se` : erreur SSL.
- Vidéos YouTube : description non récupérable.
- Formation payante de Bourrelly : non accessible. C'est là que se trouvent
  ses règles précises.
