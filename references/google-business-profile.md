# Google Business Profile — commerce et service local

Revu le 2026-09-27. Étiquettes : voir [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Levier prioritaire pour le commerce local (cf. « Commerce local » dans
[audit-framework.md](audit-framework.md)), et directement pertinent si le
projet audité sert des commerces locaux (agences, artisans...).

## Accès à l'API — conditions réelles

**ESTABLISHED** — [Prerequisites, Google Business Profile APIs](https://developers.google.com/my-business/content/prereqs)
(page mise à jour le 2026-08-28) :
- la fiche doit être **validée et active depuis plus de 60 jours** ;
- l'entreprise doit avoir **un site web** qui la représente sur la fiche ;
- la demande passe par le **formulaire de contact « GBP API »**, avec une
  **validation manuelle** par Google ;
- statut visible dans Google Cloud Console : quota de 0 requête/minute =
  pas encore approuvé, 300 = approuvé.

Ne jamais présenter l'automatisation GBP comme immédiate : prévoir le délai
d'approbation dans toute estimation. Gratuite une fois approuvée.

## Posts

**ESTABLISHED** — [Aide Google Business Profile, posts](https://support.google.com/business/answer/7342169)
(consultée le 2026-09-27) : les posts « Nouveautés » de plus de **6 mois**
sont archivés, sauf si une période est définie ; offres et événements
portent leurs propres dates. L'ancienne règle « un post expire après
7 jours », encore répandue, n'est plus celle de la documentation.

## Automatisable une fois l'accès obtenu
- Publication de posts.
- Réponses aux avis : **brouillon assisté uniquement**, jamais d'envoi
  automatique sans relecture humaine.
- Mise à jour d'informations de fiche en masse (multi-établissements).
- Suivi de performance (impressions, actions, appels).

## Ce que l'API ne couvre pas
Pas de suivi de position locale, pas de gestion de citations (annuaires) :
ces besoins restent de l'outillage tiers, payant.

## Mise en place
1. Vérifier les deux conditions d'éligibilité ci-dessus.
2. Console Google Cloud : activer les APIs « Business Profile ».
3. Soumettre le formulaire d'accès, attendre la validation.
4. OAuth 2.0 une fois approuvé.

Pas de script fourni : aucun accès GBP n'a pu être testé en conditions
réelles. À construire sur le modèle de `scripts/gsc_report.py` le jour où un
accès existe.
