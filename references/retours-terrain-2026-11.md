# Retours de terrain (août à novembre 2026)

Leçons tirées de sites réels, sans rien de propre à un seul projet. Chaque ligne porte sa date et sa source (compte rendu interne daté). Niveau de preuve : SUPPORTED (constaté sur un site, mesuré ou vérifié en ligne), sauf mention.

## Pages à retirer des résultats
- Page de vente ou page sans valeur de recherche : `noindex, follow` (pas `nofollow`, pour garder le poids des liens vers les pages importantes) ET retrait du sitemap. Demander à Google d'indexer une page qui refuse l'indexation est contradictoire. Vérifier la balise en ligne et purger le cache du CDN (03/11/2026, compte rendu SiteServi).
- Page de catégorie d'un média : 0 contenu = 404, 1 à 2 = page existante en `noindex`, 3 ou plus = indexée et dans le sitemap ; lien de menu dès le premier contenu (07/11/2026, compte rendu Vuntum).

## Plusieurs domaines pour un même site
- Les domaines secondaires renvoient vers le principal en 301 au lieu de servir le même contenu : un même contenu sur trois adresses fait déclasser deux d'entre elles (10/11/2026).
- Racine multilingue : 301 seulement quand la requête n'a pas d'en-tête de langue, 302 pour les navigateurs (07/11/2026).
- Le certificat est confié à un script qui surveille le DNS et le prend dès qu'il change, plutôt qu'à une vérification manuelle ; le renvoi peut être mis en service avant le DNS (10/11/2026).
- Vérifier le DNS auprès du serveur qui fait autorité chez le registrar (par exemple `dns1.registrar-servers.com` pour Namecheap), pas auprès d'un résolveur public : pas d'effet de cache (10/11/2026). Détail : skill `presence-locale-domaines`.

## Titres et affirmations
- Changer le titre du site sur toute la page d'accueil et le partage : noter l'ancienne et la nouvelle version avec la date pour suivre l'effet dans Google (08/11/2026).
- Une affirmation de rang (« premier média ») s'écrit sous une forme vérifiable (« l'un des premiers ») ; sources officielles et licence citées exactement (07/11/2026).

## Images et contenus
- Une même photo ne sert jamais deux contenus ; un contenu dont toutes les images sont prises s'affiche sans photo plutôt qu'avec une image reprise. Seuil de ressemblance mesuré sur des cas réels : 10 bits d'écart sur l'empreinte perceptuelle (07/11/2026).
- Un contenu rumeur ou fuite n'est jamais une mise à jour d'un contenu établi ; seuil mécanique : média nommé et au moins une source primaire ou deux médias indépendants (07/11/2026).

## Local et moteurs de réponse
- Les moteurs de réponse citent de plus en plus les annuaires locaux (Pages Jaunes dans un graphique de suivi montré le 10/11/2026, CLAIMED : à recouper). La fiche de base gratuite suffit, les options payantes n'apportent rien de mesuré.
- Une fiche Google Business en zone de service (sans adresse affichée) est introuvable par la recherche ordinaire ; la retrouver par son identifiant de lieu ou son lien Maps (03/11/2026). Détail : `google-business-profile.md`.

## Contrôles qui reviennent
- Un e-mail transactionnel qui ne part pas peut venir d'un User-Agent refusé par le CDN devant le fournisseur d'envoi : déclarer un User-Agent explicite (03/11/2026).
- Un défaut d'audit reste signalé chaque semaine tant qu'il n'est pas corrigé ; aucune liste d'exceptions (10/11/2026).
