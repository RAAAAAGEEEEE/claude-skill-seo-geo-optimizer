# Praticiens SEO français : Laurent Bourrelly et Stéphane Delgado

Revu le 2026-11-08 (posts X lus le 2026-09-28 ; Paul Vengeons et compléments Bourrelly lus le 2026-11-08, voir la section dédiée). Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

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
- L'échange de liens ou de classements, même « sur trois sites » (V10), l'achat de liens présenté comme toléré,
  l'auto-classement premier non fondé (V16), les signaux Chrome (V18) et l'avatar IA ou le faux profil d'auteur
  (B-N6) : *link spam*, tromperie ou affirmation non démontrée.

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

## Paul Vengeons (`@VengeonsP`) et Laurent Bourrelly : lecture du 2026-11-08

Sources lues le 2026-11-08 : note X du 2026-11-07 ([status/2119013491864727763](https://x.com/vengeonsp/status/2119013491864727763), « 97 % du SEO en 30 min », 20 conseils) ; article X du 2026-10-21 « How to Become an SEO Chad with AI (Full Course) » ([status/2112804448648982655](https://x.com/vengeonsp/status/2112804448648982655), texte complet par fxtwitter) ; post X du 2026-05-11 ; billets Substack des 2026-01-27, 2026-02-17 et 2026-04-22 ; page paulvengeons.fr/geo (maj 2026-10-06). Vengeons (11 357 abonnés, cofondateur de ChatSEO, qui vend un outil et des audits) se déclare premier sur « meilleur consultant SEO » et à environ 50 000 € de chiffre d'affaires mensuel (la note du 2026-10-21 dit « 30K MRR » : écart non expliqué). **Aucun de ces chiffres n'est vérifié ici.** Tout ce qui suit est **CLAIMED** (praticien, sans donnée publiée) sauf mention contraire. Le texte de Bourrelly vient de son blog (billets non datés sur la page) et de son compte `@aibloodmoon`.

| N° | Méthode (source, date) | Étiquette | Rapport à Google et usage dans le skill |
|---|---|---|---|
| V1 | **Ordre des leviers** (article 2026-10-21) : 1 intention, 2 mot-clé dans le title, 3 liens internes, 4 autorité du site, 5 backlinks vers la page ; le reste est du « polish ». Technique vérifiée une fois (PageSpeed sur une page par type, un crawl), pas en boucle | CLAIMED | Compatible : le title et les liens internes sont des pratiques documentées par Google ([SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), maj 2025-12-10). L'ordre lui-même n'est pas démontré. Sert d'ordre de lecture, jamais de priorité P0/P1 |
| V2 | **Bandes d'autorité** (2026-10-21) : DR < 20 = longue traîne ; 20 à 40 = moyenne traîne ; > 40 = têtes de requêtes ; moins de 50 domaines référents = presque rien de compétitif | CLAIMED | Le DR est une métrique d'Ahrefs, pas un signal Google. Repère de choix de cible, voir [keyword-research.md](keyword-research.md) |
| V3 | **Motifs de pages** : « X vs Y », « alternative », « service + ville » ; une intention, un type de page, plusieurs variantes seulement si chaque page a un contenu propre. Cas cité : chatseo.app de 0 à environ 150 clics hors marque par mois en 3 mois avec des pages « X vs Y » (chiffre déclaré, non vérifié) | CLAIMED | Les pages « service + ville » sont exposées à *doorway abuse* si elles ne diffèrent que par le nom de la ville ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies), maj 2026-08-28). Lui-même avoue que ses pages « consultant + ville » ont tenu 3 à 4 ans puis perdu des impressions en 2026 (date « fin mars 2026 » non vérifiée, absente des références du skill) |
| V4 | **Test d'ouverture** : chercher la requête, regarder si un concurrent a le mot-clé exact dans son title ; s'il n'y en a pas, la porte est ouverte | CLAIMED | Test manuel utile, ajouté à [keyword-research.md](keyword-research.md). Ne prouve pas que Google privilégie un title |
| V5 | **Quick wins** : pages en positions 5 à 20 ; dans Search Console, filtrer sur la page ET la requête avant de lire la position moyenne (la moyenne d'un site mélange les requêtes) | CLAIMED pour la plage ; le filtre page ET requête est un usage standard du rapport Performances de Search Console (non rouvert à la source le 2026-11-08) | Compatible. Ajouté à [keyword-research.md](keyword-research.md) |
| V6 | **Lecture de la SERP** : lire les trois premiers résultats pour l'intention, ne regarder les concurrents qu'ensuite, chercher « ce que les trois premiers n'ont pas » ; page « comme celle de Google en mieux » | CLAIMED | Rejoint BX2 (lire la page de résultats) |
| V7 | **Anatomie du title** : mot-clé exact, deux-points, une promesse, l'année, « best », environ 600 px ; la meta description sert à donner une raison de cliquer (simulateur de pixels) | CLAIMED | Google réécrit titles et descriptions quand il juge mieux ([titles](https://developers.google.com/search/docs/appearance/title-link)). Ne pas mettre une année fausse ou un « best » non fondé |
| V8 | **Liens internes** : au moins 3 à 5 liens contextuels vers une page cible, ancre exacte, jamais la même ancre pour deux pages différentes | CLAIMED pour les nombres | Compatible avec les conseils Google sur les ancres descriptives ; un nombre fixe est un paramètre, pas une exigence |
| V9 | **Backlinks** : aligner le nombre de domaines référents et le mélange d'ancres sur les trois premiers résultats ; ignorer les liens toxiques, ne pas désavouer | Le « ne pas désavouer » est ESTABLISHED ([Disavow](https://support.google.com/webmasters/answer/2648487) : outil avancé, la plupart des sites n'en ont pas besoin) ; le reste CLAIMED | Compatible |
| V10 | **Échange de liens ou de classements** : « un échange se fait sur trois sites, jamais en direct » ; « je te mets 2e, tu me mets 1er » (Substack 2026-04-22) ; achat de backlinks « interdit par Google mais pas par la loi » | CLAIMED | **Conflit** : *link spam* (« excessive link exchanges », achat de liens). Un échange triangulaire reste un échange. **Ne jamais recommander** (comme BX5 et BX6) |
| V11 | **Cadence de publication** : première page à la main, puis duplication par une IA avec un brief distinct par variante ; plafond d'une page par jour (environ 2 par semaine, 1 par semaine sur site neuf) ; « programmatic SEO réservé aux sites déjà autoritaires » | CLAIMED | Prudence cohérente avec *scaled content abuse*. À mettre en face du contrôle `publication-burst`. **Contredit** son billet du 2026-04-22 (« 1 page par jour en pilote automatique ») |
| V12 | **Registre des modifications** (« ledger ») et fichier de contexte `SITE.md` ; règle des 90 jours (ne pas rejuger une page modifiée avant 90 jours) | CLAIMED (la règle des 90 jours est son « Transition Rank », non documentée par Google) | Le registre est une bonne pratique de preuve, ajouté à [keyword-research.md](keyword-research.md). Les délais Google réels : voir [exact-match-domains.md](exact-match-domains.md) |
| V13 | **Pages zombies** : pages sans impression sur 16 mois, jamais avant 2 à 6 mois d'âge ; la cannibalisation serait « surtout un mythe » | CLAIMED | Prudent. À ne pas traduire en suppression automatique |
| V14 | **Langues** : ne pas traduire les mots-clés marché par marché, un `.com` avec un répertoire par langue | CLAIMED | Compatible avec la documentation hreflang du skill |
| V15 | **Règles pour une IA qui touche un site** : chaque nombre lu par un outil le jour même ; relire le diff (une IA a retiré en silence des tableaux de classement) ; contrôler le site réel | CLAIMED (retour d'expérience) | Utile et sans risque, ajouté à [checklist.md](checklist.md) |
| V16 | **Auto-classement** : « être premier de sa propre liste ne marche plus » (2026-11-07), il a enseigné la méthode jusqu'en juin 2026, puis retrait par Claude et échange de classement avec une agence. Billet du 2026-04-22 : l'inverse (« Mettez-VOUS n°1 ») | CLAIMED, auto-contredit | Rejoint les mesures de Lily Ray (voir [content-formats.md](content-formats.md)). Ne pas se placer premier d'un classement non fondé |
| V17 | **GEO** : « il faut d'abord avoir un bon SEO » ; suivi manuel de 3 à 5 requêtes par semaine en session privée ; `llms.txt` inutile ; Bing AI Performance « le seul outil de suivi GEO digne de ce nom » (Substack 2026-02-17) | CLAIMED ; l'outil Bing est ESTABLISHED comme fonctionnalité ([Bing, 2026-02-10](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)) | Le lien SEO puis GEO s'oppose à Ahrefs (2025-09-03 : environ 10 % de recoupement entre ChatGPT et le top 10 Google), voir [evidence.md](evidence.md). Le reste est déjà dans le skill |
| V18 | **« Google voit ces signaux, notamment avec Chrome »** (rebond, défilement) et « Google conserve environ 13 mois de mémoire des rebonds » (2026-10-21) | CLAIMED, non démontré | aucune page Google lue le 2026-11-08 ne le confirme ; **ne pas reprendre** comme fait |
| V19 | **Couche humaine** : auteur nommé, captures d'écran, verdict à la première personne | CLAIMED | Compatible avec les questions de qualité de Google ([contenu utile](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)) |

**Laurent Bourrelly : compléments (blog, billets non datés lus le 2026-11-08).**

| N° | Méthode | Étiquette | Rapport à Google et usage |
|---|---|---|---|
| B-N1 | **« Mot mystère »** : retirer le mot-clé exact d'un passage, un lecteur compétent doit deviner le sujet ; soigner les 200 à 300 premiers mots (billet 59274) | CLAIMED | Compatible (écrire pour le lecteur, pas de bourrage). Test manuel ajouté à la checklist |
| B-N2 | **« Odeur de la SERP » et faisabilité** : certaines pages de résultats sont occupées par des entités traitées comme « la réponse » (marques, encyclopédies), ce qui rend la place inatteignable pour une page ordinaire ; lire onglets, types d'URL et présence d'un AI Overview avant de produire | CLAIMED | Renforce la lecture de SERP (V6, BX2). Ajouté à [keyword-research.md](keyword-research.md) |
| B-N3 | **Le test « mon texte sur une autre page »** : si je colle mon texte sur le site d'un autre, quelqu'un s'en aperçoit-il ? Sinon, il n'apporte rien de propre | CLAIMED | Bon contrôle manuel pour *scaled content abuse*. Ajouté à la checklist |
| B-N4 | **Le lien est une affirmation** : légitime seulement si la page suivante est le prochain indice du sujet | CLAIMED | Rejoint BX3 et D9 |
| B-N5 | **Silo contre cluster** ; GEO = « rebranding » du SEO ; « les experts GEO sont du scam » (`llms.txt`, découpage en morceaux) | CLAIMED | Divergence avec Vengeons sur la longue traîne (Bourrelly : « stratégie du loser ») : l'arbitrage dépend de l'autorité du site, voir V2 |
| B-N6 | **« 6 points d'entrée par jour minimum »**, avatar IA (billet 59134), page auto-promotionnelle « meilleur SEO de France » (billet 59094) | CLAIMED | **Risque** : contenu de masse (*scaled content abuse*) et faux profil d'auteur (E-E-A-T : un auteur fictif trompe le lecteur). **Ne pas reprendre** |
| B-N7 | **Stratégie française dominante = « du Google Text et des backlinks achetés »** (billet 59274) | CLAIMED | Description d'un marché, pas une méthode. Achat de liens : voir BX5 |

**Ce que ces lectures ajoutent au skill.** Étapes manuelles (V4, V5, V6, V15, B-N1, B-N2, B-N3), un
registre des modifications (V12), des repères de cadence en CLAIMED (V11) et un renvoi vers
[exact-match-domains.md](exact-match-domains.md). **Conflits à dire au propriétaire** : V16 contredit
Vengeons lui-même (2026-04-22 contre 2026-11-07) ; V10 et la tolérance à l'achat de liens contredisent Google ;
V18 n'est pas démontré.

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
