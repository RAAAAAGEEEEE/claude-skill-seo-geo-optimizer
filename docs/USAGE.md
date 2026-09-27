# Utilisation

Retour : [README](../README.md) · Voir aussi : [CONFIGURATION](CONFIGURATION.md),
[TROUBLESHOOTING](TROUBLESHOOTING.md), [procédure du skill](../SKILL.md).

Toutes les commandes se lancent depuis le dossier du skill. Chaque commande
de ce document a été exécutée le 2026-09-28 sous Windows 11 (Git Bash,
Python 3.11), sauf mention « non exécuté ».

## Audit complet : `run_audit.py`

```bash
python scripts/run_audit.py --site https://example.com
```

Ce que fait la commande, dans l'ordre :
1. **Accueil et robots.txt.** Suit les redirections de l'accueil. Un
   robots.txt en 5xx, en 429 ou injoignable est un P0 : tout est alors
   interdit aux crawlers.
2. **Accès des crawlers** (`check_ai_access.py`). 25 crawlers de recherche
   et d'IA sont testés avec leur user-agent documenté, et comparés à un
   navigateur.
3. **Sitemaps.** Lit les lignes `Sitemap:` de robots.txt, ou `/sitemap.xml`.
   Suit les index, décompresse le gzip, contrôle la cohérence de `lastmod`.
4. **Crawl.** L'accueil, puis les URLs du sitemap (échantillonnées par
   répertoire si elles dépassent `--max-pages`), puis les liens découverts.
   Les URLs interdites par robots.txt ne sont pas visitées.
5. **Contrôles par page** : HTTP, redirections temporaires, noindex et
   nosnippet, title, description, canonical, H1, lang, JSON-LD
   (`validate_schema.py`).
6. **URLs inexistantes.** Sondées sous la racine et sous chaque rubrique :
   la réponse attendue est 404 ou 410, jamais 5xx ni 200.
7. **Cohérence.** Une URL du sitemap doit répondre 200, être indexable et
   auto-canonique. Le canonical doit viser une page indexable. Les hreflang
   doivent être réciproques, viser des pages 200, et la langue déclarée doit
   correspondre à `lang`. Contrôle aussi les title et descriptions dupliqués
   et les pages quasi vides.
8. **Maillage interne** (`linkgraph.py`). Mesure les orphelines, la
   profondeur, les liens cassés ou redirigés, les ancres, et sépare les liens
   contextuels des liens de navigation. Produit le tableau cocon/silos
   ([french-practitioners.md](../references/french-practitioners.md)).
9. **Modules optionnels**, actifs seulement si l'accès est fourni
   ([CONFIGURATION](CONFIGURATION.md)) : PageSpeed Insights, CrUX, Search
   Console, IndexNow.

Sorties dans `<out-dir>/<hôte>/` (par défaut `./seo-reports/<hôte>/`) :

| Fichier | Contenu |
|---|---|
| `audit_<AAAAMMJJTHHMMSSZ>.md` | Rapport lisible : résumé, état des modules, plan P0/P1/P2, sections détaillées, limites |
| `audit_<…>.json` | Même contenu pour les machines (`schema_version: 1`) |
| `diff_<…>.md` | Comparaison avec le rapport précédent du même dossier |
| `audit_<…>_sitemap.proposed.xml` | Sitemap proposé : seulement si une incohérence de sitemap est trouvée **et** que toutes les URLs déclarées ont été vérifiées |
| `audit_<…>_indexnow_urls.txt` | URLs nouvelles ou modifiées depuis le rapport précédent, si une clé IndexNow est fournie |

Codes de sortie :
- 0 : aucun P0 ;
- 1 : au moins un P0 ;
- 2 : accueil injoignable. Le rapport est écrit quand même, mais ne rien en
  conclure.

Options utiles :
- `--max-pages` : 60 par défaut.
- `--delay` : 0,5 s entre deux requêtes par défaut.
- `--out-dir` : dossier des rapports.
- `--no-ai-access` : ne pas tester les crawlers IA.
- `--max-depth` et `--thin-words` : seuils heuristiques.
- `--psi-pages`, `--psi-strategy` : pages mesurées par PageSpeed.
- `--gsc-site` : propriété Search Console.
- `--indexnow-key-env` : variable qui contient la clé IndexNow de ce site.
- `--indexnow-submit` : soumission IndexNow (action externe).
- `--no-diff` : ne pas comparer au rapport précédent.

Liste complète : `python scripts/run_audit.py --help`.

Exemple réel (site anonymisé, 2026-09-27 22:32 UTC, sans clé) : P0=0, P1=1,
P2=4 ; 25 pages et 80 requêtes en 40 à 50 s. Le P1 est `/fr/guides`, présente
dans le sitemap mais liée par aucune page.

## Comparer deux rapports : `diff_reports.py`

```bash
python scripts/diff_reports.py --dir seo-reports/example.com          # les deux derniers
python scripts/diff_reports.py ancien.json nouveau.json --out diff.md
```
Le diff liste :
- les constats nouveaux, résolus, et ceux dont les URLs ont changé ;
- l'évolution des chiffres : P0/P1/P2, pages, orphelines, liens cassés,
  score PageSpeed, CrUX, clics et impressions Search Console.

Code de sortie 1 si un P0 est apparu.

`run_audit.py` écrit ce diff tout seul à chaque passage, s'il trouve un
rapport précédent.

Pour régénérer le Markdown d'un ancien JSON :
`python scripts/report_markdown.py seo-reports/example.com/audit_<…>.json`.

## Planifier l'audit

La création d'une tâche planifiée modifie une configuration persistante de
la machine. Le skill ne la crée **jamais** sans l'accord du propriétaire.

### Linux (cron), par exemple sur un VPS

1. Copier [.env.example](../.env.example) hors du dépôt, par exemple dans
   `~/secrets/seo-audit.env` avec les droits 600, et le remplir.
2. Vérifier la commande à la main. La forme suivante a été exécutée avec un
   fichier d'environnement de test :
   ```bash
   set -a; . ~/secrets/seo-audit.env; set +a; python3 ~/.claude/skills/seo-geo-optimizer/scripts/run_audit.py --site https://example.com --out-dir ~/seo-reports
   ```
3. Ajouter la ligne avec `crontab -e`. Exemple : chaque lundi à 06:00, avec
   un journal. **Non exécuté** : c'est une configuration persistante.
   ```cron
   0 6 * * 1 bash -c 'set -a; . ~/secrets/seo-audit.env; set +a; python3 ~/.claude/skills/seo-geo-optimizer/scripts/run_audit.py --site https://example.com --out-dir ~/seo-reports' >> ~/seo-reports/cron.log 2>&1
   ```

Pour plusieurs sites, une ligne par site. Chaque site a son `--out-dir`
commun et sa variable IndexNow : `--indexnow-key-env INDEXNOW_KEY_EXEMPLE`.

### Windows (Planificateur de tâches)

**Non exécuté** : c'est une configuration persistante. Mettre les variables
dans l'environnement utilisateur, puis :
```powershell
schtasks /Create /SC WEEKLY /D MON /ST 07:00 /TN "seo-audit-example" /TR "python %USERPROFILE%\.claude\skills\seo-geo-optimizer\scripts\run_audit.py --site https://example.com --out-dir %USERPROFILE%\seo-reports"
```

### Tâche planifiée Claude Code

Dans Claude Code (application de bureau, tâches planifiées), demander par
exemple : « chaque lundi, lance `python scripts/run_audit.py --site
https://example.com --out-dir ~/seo-reports` depuis le dossier du skill,
puis résume le `diff_*.md` le plus récent et signale tout nouveau P0 ».

L'intérêt par rapport à cron : Claude lit le diff et propose les
corrections. Le **GO** reste nécessaire avant tout changement de code.

Une tâche planifiée qui s'exécute dans le cloud (`/schedule`) n'a pas
accès aux fichiers ni aux variables de la machine locale. Elle ne convient
donc que pour l'audit sans clé, ou avec des secrets configurés côté cloud.

### Ne pas planifier sans accord

`--indexnow-submit` dans une tâche planifiée envoie des URLs à des tiers à
chaque passage. Ne l'ajouter qu'après accord explicite du propriétaire.

## Autres scripts

| Besoin | Commande |
|---|---|
| Accès des crawlers à une page précise | `python scripts/check_ai_access.py https://example.com/page` |
| Rapport sur une liste d'URLs choisie | `python scripts/generate_report.py --urls urls.txt --out-prefix AUDIT_GEO` |
| Valider du JSON-LD (fichier ou URL) | `python scripts/validate_schema.py tests/fixtures/schema_cases.html` |
| PageSpeed d'une page | `python scripts/pagespeed.py https://example.com/` (avec `PAGESPEED_API_KEY`) |
| CrUX d'une origine | `python scripts/crux_report.py --origin https://example.com` (avec `CRUX_API_KEY`) |
| Vérifier une clé IndexNow sans rien soumettre | `python scripts/indexnow_submit.py --host example.com --urls urls.txt --dry-run` (avec `INDEXNOW_KEY`) |
| Générer sitemap et robots.txt | `python scripts/generate_sitemap.py pages.json --domain https://example.com --write-robots` |
