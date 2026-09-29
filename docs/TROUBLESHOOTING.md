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
| `search_console.py` sort avec le code 2 | Ni `GSC_SERVICE_ACCOUNT_FILE` (fichier existant) ni `GSC_ACCESS_TOKEN` | Donner le chemin absolu de la clé JSON dans la variable ([gsc-access.md](../references/gsc-access.md), étape 8). |
| `Erreur Search Console : HTTP 403` | Compte de service absent de la propriété, ou propriété mal écrite (`sc-domain:example.com` vs `https://example.com/` avec barre finale) | `python scripts/search_console.py sites` liste les propriétés accessibles et le niveau ; recopier la valeur exacte. |
| `HTTP 403` sur `submit-sitemap` seulement | Niveau insuffisant pour l'écriture | Passer le compte en **Propriétaire** ([gsc-access.md](../references/gsc-access.md#propriétaire-ou-accès-complet-)). |
| Message « has not been used in project » ou « disabled » | API non activée dans le projet Google Cloud | Étape 2 du tutoriel, puis attendre quelques minutes. |
| Création de clé refusée dans Google Cloud | Contrainte d'organisation `iam.disableServiceAccountKeyCreation` | Créer le projet hors organisation (compte personnel) ou demander une exemption à l'administrateur ([doc Google](https://cloud.google.com/iam/docs/keys-create-delete?hl=fr)). |
| `inspect` : `quota_stopped: true` | 2 000 inspections/jour ou 600/minute par propriété atteints | Relancer le lendemain ; baisser `--max-inspect`. Les résultats déjà obtenus sont gardés dans l'état. |
| `url_discovery.py` : `websub: error` | Hub injoignable ou URL du flux refusée par le hub | Vérifier que le flux déclare `rel="self"` avec son URL publique exacte, puis relancer ; les URL restent en attente. |
| `url_discovery.py` : P1 « sans lien depuis l'accueil » alors que le menu lie la page | Lien rendu en JavaScript, ou page liée depuis une rubrique non fournie | Vérifier le HTML servi (`curl`) ; ajouter `--hub-page <rubrique>`. |
| `url_discovery.py` : « premier passage », rien annoncé | Premier passage = état de référence | Normal. Pour annoncer tout de suite des pages précises : `--urls fichier.txt`. |
| Constat `indexnow-key-invalid` | `/<clé>.txt` absent de la racine ou contenu différent | Publier le fichier à la racine, contenant uniquement la clé. |
| « Contrôles contextuels désactivés » | Le HTML n'a ni `<main>`, ni `<article>`, ni `<nav>` | Baliser les zones (utile aussi pour l'accessibilité), ou lire le maillage sans la distinction contextuelle. |
| Beaucoup d'orphelines alors que le menu lie tout | Menu rendu en JavaScript, ou crawl incomplet (`crawl_complete: false`) | Vérifier le HTML servi (`curl`). Augmenter `--max-pages`. |
| Le crawl ignore des pages | Pages interdites par robots.txt (listées dans `skipped_by_robots`), URLs à paramètres (`--include-query`), fichiers non HTML | Comportement voulu. Ajuster les options si besoin. |
| Accès crawlers : 403 pour un bot, 200 pour le navigateur | Règle CDN/WAF par user-agent | Voir [cloudflare-ai-access.md](../references/cloudflare-ai-access.md). Confirmer dans les journaux. |
| `crawler_logs.py` : « Aucune ligne reconnue » (code 2) | Format de journal autre que *combined* ou JSON lines | Exporter au format *combined*, ou en JSON lines avec `remote_addr`, `time`, `request`, `status`, `http_user_agent`. |
| `crawler_logs.py` : liste d'un fournisseur en `erreur` | Réseau, ou URL déplacée par le fournisseur | Relancer ; sinon vérifier l'URL dans la page « bots » du fournisseur et mettre à jour `RANGES`. En attendant, ses requêtes sont « non vérifiables ». |
| `glossary_check.py audit` trouve 0 ou 1 terme | Hub qui lie une page par terme, sans `<dt>`/`<dfn>` | Ajouter `--term-links '<motif d'URL des définitions>'`. |
| Git Bash : `--term-links '/fr/definition/'` ne trouve rien | Git Bash convertit un argument qui commence par `/` en chemin Windows | Préfixer la commande par `MSYS_NO_PATHCONV=1`, ou écrire le motif sans `/` initial (`fr/definition/`). |
| Caractères accentués illisibles dans la console Windows | Console en cp1252 | Les scripts forcent UTF-8 sur stdout. Sinon : `set PYTHONIOENCODING=utf-8`. |
