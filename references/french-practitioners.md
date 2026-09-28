# Praticiens SEO français : Laurent Bourrelly et Stéphane Delgado

Revu le 2026-09-28. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

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
cocon restent en ligne sous `/blog/`.

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

## Ce qui n'entre pas

- Le PBN ou « cocon off-site » (B7) et toute mention achetée ou fabriquée
  (limite de D3) : *link spam*.
- La déclinaison d'un sujet en dizaines de pages sans valeur propre (B7) :
  *scaled content abuse*.
- Les seuils présentés comme des règles : 150 mots (D6), nombre de liens par
  page (D9). Ils restent des paramètres, jamais des exigences.
- Les statistiques sans source (D8).

## Posts X : tentative du 2026-09-28

Le propriétaire a autorisé la lecture des posts via ses identifiants API X
(v2, jeton applicatif), limitée aux 100 derniers posts originaux de chacun.

| Personne | Compte lié depuis son propre site | Vérification |
|---|---|---|
| Laurent Bourrelly | `@laurentbourelly` (un seul « r »), lien « Twitter » de [contact.php](https://www.laurentbourrelly.com/contact.php) et de la page de formation | lu le 2026-09-28 |
| Stéphane Delgado | `@stephdelgado`, liens du pied de page de [stephanedelgado.fr](https://www.stephanedelgado.fr/) | lu le 2026-09-28. Un moteur de recherche affiche aussi un profil `@Stephanedelgado` (botSEO) : lien du site peut-être ancien, **non vérifié** |

**Résultat : aucun post lu.** Les deux appels de recherche de compte
(`GET /2/users/by/username/:u`) ont renvoyé **401 Unauthorized** : le jeton
présent sur le serveur est refusé par l'API. Aucun appel de timeline n'a
donc été fait (2 appels au total). Rien de ce fichier ne vient de X.

Pour relancer : régénérer le *bearer token* dans la console développeur X,
le remplacer sur le serveur, puis refaire les 4 appels (2 comptes × recherche
+ timeline). Vérifier d'abord le compte actuel de Stéphane Delgado.

## Sources non lues

- **X (Twitter)** : voir la section précédente (jeton refusé, 401).
- LinkedIn et Malt de Stéphane Delgado : mur de connexion, non ouverts.
- Interview de Bourrelly sur `cocon.se` : erreur SSL.
- Vidéos YouTube : description non récupérable.
- Formation payante de Bourrelly : non accessible. C'est là que se trouvent
  ses règles précises.
