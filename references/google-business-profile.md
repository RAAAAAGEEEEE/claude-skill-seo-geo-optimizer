# Google Business Profile — pertinent pour tout commerce/service local

Levier prioritaire pour le commerce local (cf. "Commerce local" dans
[audit-framework.md](audit-framework.md)), et directement pertinent si le
projet audité sert des commerces locaux (agences, artisans...).

## État de l'API (vérifié juillet 2026)
L'API GBP est active et maintenue, scindée en plusieurs APIs distinctes par
fonction (fiches, avis, posts, photos, performance).

**Piège à connaître avant de promettre une automatisation** : l'accès à
l'API nécessite une **validation manuelle par Google**, pas juste une
activation dans Google Cloud Console. Ne pas présenter l'automatisation GBP
comme immédiate — prévoir un délai d'approbation dans toute estimation.
Gratuite une fois approuvée.

## Automatisable une fois l'accès obtenu
- Publication de posts (Google recommande ~1/semaine, 4-5/mois ; les posts
  standard expirent après 7 jours, les offres/événements durent jusqu'à leur
  date de fin).
- Réponses aux avis (brouillon assisté, jamais d'envoi automatique sans
  relecture — même principe que les brouillons d'outreach ailleurs dans cet
  écosystème de skills).
- Mise à jour d'informations de fiche en masse (multi-établissements).
- Suivi de performance (impressions, actions, appels).

## Ce que l'API ne couvre pas
Pas de suivi de position/ranking local, pas de gestion de citations
(annuaires), pas de mise à jour en masse au-delà de ce que l'API expose
explicitement — ces besoins restent outillage tiers (payant) si nécessaires.

## Mise en place
1. Console Google Cloud > activer les APIs "Business Profile".
2. Soumettre le formulaire d'accès (validation manuelle Google, délai
   variable).
3. OAuth 2.0 une fois approuvé.

Pas de script fourni dans ce skill pour l'instant (pas de credential GBP
disponible pour tester en conditions réelles, contrairement à GSC) — à
construire sur le même modèle que `gsc_report.py` une fois un accès obtenu.
