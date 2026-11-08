# Backlinks — cadre d'évaluation technique

Revu le 2026-09-27.

Ce fichier sert à **évaluer** un lien existant ou une opportunité de lien
(qualité, risque, conformité) — pas à en trouver ou à en acquérir. La
prospection, le choix des cibles éditoriales, la rédaction et l'envoi de
pitchs/outreach relèvent du skill `seo` (`/seo`), pas de ce skill.

## Interne vs externe
- **Liens internes** (sous-domaines d'un même domaine racine, ex.
  `client-x.example.com` → `example.com`) : valeur SEO quasi nulle,
  c'est de l'auto-référencement, pas un signal d'autorité tierce. Ne jamais
  les présenter comme des backlinks dans un rapport ou à un client.
- **Liens externes** (autre domaine, autre propriétaire réel) : seule
  source de vraie valeur SEO/GEO.

## Suivi vs nofollow / sponsored / ugc
Google traite `nofollow`, `sponsored` et `ugc` comme des **indications**
(« hints ») pour le classement depuis septembre 2019, et pour le crawl depuis
le 2020-03-01 (ESTABLISHED, [Google, 2019-09](https://developers.google.com/search/blog/2019/09/evolving-nofollow-new-ways-to-identify)) : ces liens transmettent peu ou pas d'autorité, sans garantie
dans un sens ou dans l'autre. Un lien payé ou sponsorisé **doit** porter
`sponsored` (ou `nofollow`). Vérifier avec
[scripts/check_backlinks.sh](../scripts/check_backlinks.sh) plutôt que de
supposer.

Côté moteurs IA, les **mentions** de marque (même sans lien) corrèlent plus
à la visibilité dans AI Overviews que les backlinks (Ahrefs, 2025, CLAIMED
méthode publiée, corrélation) : un lien n'est pas le seul signal de
réputation. Voir [evidence.md](evidence.md).

## Variation des ancres
Des ancres de lien identiques répétées sur de nombreux sites externes sont
un signal artificiel pour Google (sur-optimisation). Viser une diversité
naturelle : nom de marque, URL nue, texte descriptif générique, texte de
correspondance partielle — jamais la même expression de mot-clé exact
partout.

## Risque PBN (Private Blog Network)
Si une même entité possède/gère plusieurs domaines qui se lient entre eux,
Google peut détecter le réseau via des empreintes communes (registrar,
WHOIS, plage d'IP d'hébergement, template identique) et traiter l'ensemble
comme un réseau artificiel — risque de pénalité manuelle ou algorithmique
sur tous les domaines concernés, pas seulement celui visé.
- Ne jamais faire se lier entre eux les différents SaaS/sites d'un même
  propriétaire sans raison éditoriale réelle qui existerait même sans
  objectif SEO (cf. garde-fous du skill `seo`).
- Si plusieurs domaines sont légitimement liés (marque ombrelle), varier les
  empreintes techniques et être transparent sur la propriété plutôt que de
  la dissimuler.

## Annuaires / directories
Utiles pour l'autorité de domaine, pas seulement pour le trafic direct :
- Prioriser par autorité du domaine annuaire et par pertinence
  linguistique/géographique de la cible.
- Un annuaire hors-langue ou hors-pays reste utile pour l'autorité globale
  du domaine, même si son trafic ne convertit jamais — ne pas l'écarter
  seulement parce que la audience ne correspond pas.
- **Ne jamais automatiser la soumission** (formulaires + CAPTCHA fragiles,
  risque de ban IP/compte sur l'annuaire). Saisie manuelle uniquement.

## Désaveu, échanges et classements payants (ajout du 2026-11-08)
- **Désaveu** : outil « advanced » de Google ; « most sites will not need to use this tool »
  ([aide Search Console](https://support.google.com/webmasters/answer/2648487), page sans date affichée, lue le
  2026-11-08). Ne pas désavouer par principe les liens « toxiques » signalés par un outil tiers (ESTABLISHED
  pour la position de Google ; Paul Vengeons dit la même chose, CLAIMED).
- **Échange de liens ou de classements** (« je te mets 2e, tu me mets 1er », échange « sur trois sites »,
  recommandé par Vengeons, Substack 2026-04-22 et article X 2026-10-21) : relève de *link spam* ("excessive link
  exchanges", pages de partenaires "exclusively for the sake of cross-linking", [spam policies](https://developers.google.com/search/docs/essentials/spam-policies),
  maj 2026-08-28). Un échange triangulaire reste un échange. **Ne jamais recommander.**
- **Placement payant dans un classement tiers** : un lien payé pour le classement est du *link spam* ; si la
  mention est commerciale, l'étiqueter (`rel="sponsored"`) et la déclarer comme telle.
- **Achat de backlinks présenté comme toléré** (« interdit par Google mais pas par la loi », Vengeons) : vrai que
  la loi ne l'interdit pas, sans effet sur la politique de Google. **Ne jamais recommander** (voir BX5 dans
  [french-practitioners.md](french-practitioners.md)).

## À bannir sans exception
- Achat de backlinks, fermes de liens, réseaux d'échange massif —
  politique « Link spam » de Google. Politiques anti-spam actuelles :
  [spam-policies.md](spam-policies.md).
- Toute automatisation de soumission de masse vers des annuaires ou
  plateformes tierces.

## Ce qui attire des liens naturellement (repère, pas une action de ce skill)
Le contenu qui génère des backlinks sans démarchage actif (outils gratuits
interactifs, articles de référence sourcés et datés) est aussi ce qui a le
plus de chances d'être cité par les moteurs génératifs — cf. les signaux GEO
dans [audit-framework.md](audit-framework.md#signaux-geo-retrieval-par-ia-génératives)
et [evidence.md](evidence.md).
**Produire ce type d'actif citable est le travail du skill `seo`** (phase
"production de l'actif citable" de `/seo`) — ce skill-ci se limite à
vérifier qu'un actif déjà publié respecte les fondamentaux techniques
(schema, structure, E-E-A-T) une fois que `/seo` l'a produit.
