# Politique de sécurité

## Surface
Les scripts font des requêtes HTTP vers le site audité. Ils peuvent aussi
appeler des API Google et IndexNow, si des accès sont fournis par
l'environnement. Ils manipulent des clés d'API et un fichier de compte de
service. Détail des flux : [docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md).

## Versions suivies
Seule la dernière version publiée (voir [CHANGELOG.md](CHANGELOG.md)) reçoit
des correctifs.

## Signaler une vulnérabilité
Ne pas ouvrir d'issue publique. Utiliser le signalement privé de GitHub
(onglet **Security** > **Report a vulnerability**) sur le dépôt du skill. Si
ce canal n'est pas activé, ouvrir une issue qui demande seulement un contact,
**sans** détail technique.

Exemples de sujets à signaler :
- une clé ou un jeton qui apparaîtrait dans une sortie, un journal ou une
  erreur ;
- une requête envoyée vers un tiers sans option explicite ;
- un crawl qui ne respecterait pas robots.txt ;
- une injection dans le Markdown généré à partir du contenu d'un site
  audité.

## Bonnes pratiques d'utilisation
- Clés dans l'environnement ou dans un fichier hors du dépôt (droits 600),
  jamais en argument.
- Compte de service Search Console : niveau choisi en connaissance de
  cause ([gsc-access.md](references/gsc-access.md#propriétaire-ou-accès-complet-)),
  clé révoquée dès qu'elle a pu fuiter.
- Ne pas planifier `--indexnow-submit` ni `url_discovery.py --submit` sans
  accord du propriétaire du site.
