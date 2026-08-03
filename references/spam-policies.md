# Politiques anti-spam Google — ce qu'il ne faut jamais recommander

Liste officielle actuelle (source primaire :
[Google Search Central](https://developers.google.com/search/docs/essentials/spam-policies),
16 catégories). Le point important pour ce skill : la mise à jour de
juin 2026 **n'a ajouté aucune nouvelle catégorie** — c'est un raffinement de
la détection existante, pas un changement de règles. Les catégories les plus
pertinentes pour un audit SEO/GEO courant :

- **Scaled content abuse** : « de nombreuses pages générées dans le but
  principal de manipuler le classement, pas d'aider l'utilisateur ». C'est
  la catégorie la plus activement sanctionnée depuis 2024, et elle recoupe
  de plus en plus le contenu IA produit en masse sans édition humaine.
  **Pertinent directement pour ce skill** : ne jamais recommander de générer
  du contenu à grande échelle sans révision éditoriale réelle, même pour du
  contenu "citable" GEO.
- **Expired domain abuse** : racheter un domaine expiré pour son autorité et
  y héberger du contenu sans rapport ou de faible valeur. Une redirection
  301 depuis un domaine expiré reste défendable **si l'alignement
  thématique est réel** entre source et destination — critère qui
  détermine désormais l'abus, pas la redirection elle-même.
- **Site reputation abuse** : publier du contenu tiers sur un site établi
  principalement pour profiter de son autorité existante (ex. une section
  "coupons" ou "avis" sous-traitée à un tiers sur un site d'actualité).
  Pertinent si un projet envisage d'héberger du contenu partenaire.
- **Link spam** : achat, échange ou automatisation de liens dans un but de
  manipulation — couvre ce que [backlinks.md](backlinks.md) bannit déjà
  (fermes de liens, PBN, achat de dofollow).
- **Thin affiliation** : contenu affilié copié des descriptions produit du
  marchand sans valeur ajoutée ni contenu original.
- **Cloaking, sneaky redirects, hidden text, keyword stuffing, doorway
  abuse** : bases classiques, déjà implicitement exclues par les
  recommandations on-page de ce skill.

Liste complète et définitions exactes : voir la source primaire ci-dessus,
ne pas se fier à des résumés de blogs SEO qui datent vite sur ce sujet.
