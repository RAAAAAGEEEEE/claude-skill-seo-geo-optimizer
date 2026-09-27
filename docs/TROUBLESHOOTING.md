# Dépannage

Retour : [README](../README.md) · Voir aussi : [CONFIGURATION](CONFIGURATION.md),
[LIMITATIONS](LIMITATIONS.md).

| Symptôme | Cause probable | Que faire |
|---|---|---|
| `run_audit.py` sort avec le code 2 | L'accueil ne répond pas 200 : panne, blocage de votre IP, DNS, TLS | Ouvrir l'URL dans un navigateur. Relancer quand le site répond. Ne rien conclure du rapport. |
| Module `pagespeed` en `skipped` | `PAGESPEED_API_KEY` absente | Voir [CONFIGURATION](CONFIGURATION.md#obtenir-les-accès). |
| `pagespeed: error -- PSI HTTP 400: API key not valid` | Clé invalide ou API non activée sur le projet | Activer « PageSpeed Insights API » pour la clé. |
| `PSI HTTP 429` ou `Quota exceeded` | Quota dépassé, surtout sans clé | Fournir une clé, ou baisser `--psi-pages`. |
| `crux: ran -- aucune donnée terrain` | Trafic Chrome insuffisant sur 28 jours | Normal pour un petit site : ce n'est pas un problème de performance. |
| `search_console: skipped -- GSC_SERVICE_ACCOUNT_FILE pointe vers un fichier introuvable` | Chemin erroné | Donner un chemin absolu vers le JSON du compte de service. |
| `search_console: skipped -- dépendance manquante` | `google-auth` ou `requests` absent | `pip install google-auth requests` |
| `search_console: error -- HTTPError 403` | Le compte de service n'est pas utilisateur de la propriété | L'ajouter dans Search Console > Paramètres > Utilisateurs ([gsc-access.md](../references/gsc-access.md)). |
| Constat `indexnow-key-invalid` | `/<clé>.txt` absent de la racine ou contenu différent | Publier le fichier à la racine, contenant uniquement la clé. |
| « Contrôles contextuels désactivés » | Le HTML n'a ni `<main>`, ni `<article>`, ni `<nav>` | Baliser les zones (utile aussi pour l'accessibilité), ou lire le maillage sans la distinction contextuelle. |
| Beaucoup d'orphelines alors que le menu lie tout | Menu rendu en JavaScript, ou crawl incomplet (`crawl_complete: false`) | Vérifier le HTML servi (`curl`). Augmenter `--max-pages`. |
| Le crawl ignore des pages | Pages interdites par robots.txt (listées dans `skipped_by_robots`), URLs à paramètres (`--include-query`), fichiers non HTML | Comportement voulu. Ajuster les options si besoin. |
| Accès crawlers : 403 pour un bot, 200 pour le navigateur | Règle CDN/WAF par user-agent | Voir [cloudflare-ai-access.md](../references/cloudflare-ai-access.md). Confirmer dans les journaux. |
| Caractères accentués illisibles dans la console Windows | Console en cp1252 | Les scripts forcent UTF-8 sur stdout. Sinon : `set PYTHONIOENCODING=utf-8`. |
