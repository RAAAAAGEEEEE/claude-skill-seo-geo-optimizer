# Backlinks — cadre générique

## Interne vs externe
- **Liens internes** (sous-domaines d'un même domaine racine, ex.
  `client-x.siteservi.com` → `siteservi.com`) : valeur SEO quasi nulle,
  c'est de l'auto-référencement, pas un signal d'autorité tierce. Ne jamais
  les présenter comme des backlinks dans un rapport ou à un client.
- **Liens externes** (autre domaine, autre propriétaire réel) : seule
  source de vraie valeur SEO/GEO.

## Dofollow vs nofollow
Un lien `nofollow` (ou `sponsored`/`ugc`) transmet peu de valeur
d'autorité — un lien est utile pour le PageRank principalement s'il est
cliquable **et** dofollow. Vérifier avec
[scripts/check_backlinks.sh](../scripts/check_backlinks.sh) plutôt que de
supposer.

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
  objectif SEO (cf. garde-fous du skill `SEO`).
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

## À bannir sans exception
- Achat de backlinks, fermes de liens, réseaux d'échange massif —
  pénalité Google Search Central documentée (Link Spam / netlinking
  manipulateur).
- Toute automatisation de soumission de masse vers des annuaires ou
  plateformes tierces.

## Ce qui attire des liens naturellement
Le contenu qui génère des backlinks sans démarchage actif :
- Outils gratuits interactifs (calculateurs, générateurs) directement
  utilisables sans inscription.
- Articles de référence sourcés et datés (études de prix, benchmarks,
  checklists) — cf. le levier "Autorité / entités" et les signaux GEO dans
  [audit-framework.md](audit-framework.md#signaux-geo-retrieval-par-ia-génératives).
- Ce type de contenu est aussi ce qui a le plus de chances d'être cité par
  les moteurs génératifs (GEO) — les deux objectifs (backlinks + citations
  IA) convergent sur le même type d'actif.
