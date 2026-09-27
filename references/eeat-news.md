# E-E-A-T et signaux d'éditeur (médias, sites de référence)

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

## Ce que Google dit d'E-E-A-T (ESTABLISHED)

- « E-E-A-T itself isn't a specific ranking factor » : Google s'appuie sur
  des signaux qui repèrent un contenu fiable ; la confiance est le pilier
  principal ([helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), maj 2025-12-10 ;
  [consignes des évaluateurs](https://static.googleusercontent.com/media/guidelines.raterhub.com/en//searchqualityevaluatorguidelines.pdf), version 2025-09-11).
- Questions « Who, How, Why » : qui a écrit (signature menant à une page
  auteur), comment (divulguer l'automatisation, l'IA), pourquoi (aider le
  lecteur, pas manipuler le classement).
- L'IA n'est ni bonne ni mauvaise en soi ; la production de masse à faible
  valeur est du **scaled content abuse** (politique anti-spam qui cite
  nommément l'IA générative, maj 2026-08-28).
- Les notes des évaluateurs n'agissent pas directement sur le classement.

## Signaux vérifiables dans un audit

À cocher manuellement (non automatisable, cf. [checklist.md](checklist.md)) :
- Page À-propos réelle ; mentions légales complètes (éditeur, hébergeur,
  immatriculation si applicable, contact).
- Signature sur chaque contenu éditorial, menant à une page auteur ;
  `author.url` (ou `sameAs`) dans le JSON-LD Article — c'est ce que Google
  documente pour désambiguïser l'auteur ([Article](https://developers.google.com/search/docs/appearance/structured-data/article), maj 2026-09-08).
- Dates de publication et de mise à jour visibles, cohérentes avec le
  balisage et le sitemap.
- Politique de corrections publique et journal des corrections.
- Divulgation de l'usage d'outils d'IA quand il existe.

## Google Actualités, Discover (ESTABLISHED)

- Google Actualités exige transparence : dates et signatures claires,
  informations sur les auteurs, la publication, l'éditeur et la société
  derrière, coordonnées ([règles](https://support.google.com/news/publisher-center/answer/6204050)).
- Discover : mêmes exigences de dates, auteur, éditeur, contact ; pas de
  titre trompeur ; violations répétées = inéligibilité.
- Pas de soumission à Google Actualités (inclusion automatique) ; détails
  dans [google-ai-features.md](google-ai-features.md#google-actualités--top-stories).

## Balisage d'éditeur : utile, mais pas un levier Google

- schema.org `NewsMediaOrganization` définit exactement 11 propriétés :
  `actionableFeedbackPolicy`, `correctionsPolicy`, `diversityPolicy`,
  `diversityStaffingReport`, `ethicsPolicy`, `masthead`,
  `missionCoveragePrioritiesPolicy`, `noBylinesPolicy`,
  `ownershipFundingInfo`, `unnamedSourcesPolicy`,
  `verificationFactCheckingPolicy` ; `publishingPrinciples` vit sur
  Organization/CreativeWork/Person (schema.org 30.1, 2026-09-16).
- **Google n'en documente aucune** dans ses pages Article ou Organization
  (ESTABLISHED par absence, 2026-09-08). Elles restent correctes pour
  décrire l'entité, à condition que **chaque URL pointe vers une page qui
  contient réellement la politique nommée** : faire pointer
  `diversityPolicy` vers une page méthodologie qui ne parle pas de
  diversité est un balisage inexact.
- The Trust Project : 8 indicateurs (Best Practices, Journalist Expertise,
  Labels, References, Methods, Locally Sourced, Diverse Voices, Actionable
  Feedback) — liste ESTABLISHED ; l'usage revendiqué par Google, Facebook,
  Bing est **CLAIMED** (non daté, aucune doc Google actuelle).
- Journalism Trust Initiative : CWA 17493 du CEN (2019), pas une norme ISO ;
  aucune plateforme nommée comme utilisatrice.

## Entité et désambiguïsation
- `Organization` avec `logo`, `url`, `sameAs` (profils officiels, élément
  Wikidata s'il existe) sur la page d'accueil.
- `WebSite` avec `name` (et `alternateName`) sur la page d'accueil : c'est
  ce que Google utilise pour le **nom du site** affiché dans les résultats
  (la sitelinks search box a disparu en 2024, pas le nom de site).
