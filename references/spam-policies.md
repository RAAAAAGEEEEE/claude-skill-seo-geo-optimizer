# Politiques anti-spam Google — ce qu'il ne faut jamais recommander

Revu le 2026-09-27, état des mises à jour complété le 2026-11-08. Source primaire :
[Google Search Central, spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
(maj 2026-08-28). **ESTABLISHED.**

État : **16 politiques nommées**, plus une section « Other practices »
(retraits légaux, retraits d'informations personnelles, contournement des
règles, arnaques). Aucune nouvelle catégorie en 2026 ; deux renommées
(« Malicious practices », « Site reputation policy »). Mises à jour de
détection récentes : spam updates de juin (24-26), août (18-21) et
septembre 2026 (démarrée le 24, en cours au 2026-09-27).

**État au 2026-11-08** : page des spam policies toujours « Last updated 2026-08-28 UTC » ; journal des mises à
jour de Google : dernière entrée le 2026-10-26, sans rapport avec ces politiques. Selon des relevés tiers (tableau
de bord Google non relu), la spam update de septembre a couru du 2026-09-24 au 2026-10-08 et aucune mise à jour
n'était confirmée en octobre ni début novembre (au 2026-11-06). Cas des domaines à mot-clé exact, des réseaux de
sites et des stratégies « achat de domaines puis attente » : [exact-match-domains.md](exact-match-domains.md).

Les plus pertinentes pour un audit SEO/GEO :

- **Scaled content abuse** : beaucoup de pages produites surtout pour
  manipuler le classement. La définition cite nommément l'IA générative.
  Google range explicitement dans cette catégorie le fait de créer une page
  par requête « fan-out » pour manipuler les réponses IA (guide IA, maj
  2026-07-10). Ne jamais recommander de produire du contenu en masse sans
  révision éditoriale réelle, même « pour être cité ».
- **Site reputation abuse** : contenu tiers hébergé pour profiter de
  l'autorité d'un site établi. Depuis le 2026-08-30, les actions manuelles
  de cette politique ne s'appliquent plus aux utilisateurs de l'EEE ; la
  politique reste en vigueur ailleurs et la détection algorithmique aussi.
- **Expired domain abuse** : racheter un domaine expiré pour son autorité
  et y mettre un contenu sans rapport.
- **Link spam** : achat, échange ou automatisation de liens —
  cf. [backlinks.md](backlinks.md).
- **Malicious practices** : inclut le « back button hijacking »,
  sanctionné depuis le 2026-06-15.
- **Thin affiliation**, **cloaking**, **sneaky redirects**, **hidden
  text**, **keyword stuffing**, **doorway abuse** : bases classiques.

Application à un petit site (contrôles H1 à H11, doorways et pages ville) :
[helpful-content-small-site.md](helpful-content-small-site.md). Définition citée de *doorway abuse* :
« multiple domain names or pages targeted at specific regions or cities that funnel users to one page ».

Liste complète et définitions exactes : la source primaire ci-dessus, pas
un résumé de blog.
