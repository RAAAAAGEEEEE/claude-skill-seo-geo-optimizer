# Architecture

Retour : [README](../README.md) · Voir aussi : [USAGE](USAGE.md),
[LIMITATIONS](LIMITATIONS.md).

## Trois couches

1. **`SKILL.md`** : la procédure que suit Claude (PLAN → FIX → VERIFY). Elle
   est courte et renvoie vers le reste. C'est le seul fichier chargé
   d'office.
2. **`references/`** : les règles datées et sourcées, avec leur étiquette
   ESTABLISHED / SUPPORTED / CLAIMED. Claude ne les charge qu'au besoin.
3. **`scripts/`** : tout ce qui se mesure sans humain.

Certaines références ne pilotent aucun script : elles servent au jugement
humain de l'étape 3 de la procédure. C'est le cas de
[content-formats.md](../references/content-formats.md) (quels formats de
contenu publier selon le type de site) : choisir un format est une décision
éditoriale, qu'aucun script ne peut vérifier.

## Flux de `run_audit.py`

```
run_audit.py
 ├─ htmlsignals.fetch_signals   accueil, puis chaque page (redirections, meta, liens <a>, mots)
 ├─ check_ai_access             robots.txt (robotstxt.py, RFC 9309) + 25 crawlers (ai_bots.py)
 ├─ sitemaps.discover           robots.txt Sitemap:, index, gzip, lastmod
 ├─ crawl                       sitemap d'abord, puis liens découverts ; respecte robots.txt
 ├─ audit_rules.page_checks     constats par page (+ validate_schema.validate_blocks)
 ├─ sondes 404                  racine + une par rubrique
 ├─ cohérence                   sitemap / canonical / hreflang / langue / doublons / pages vides
 ├─ linkgraph.analyze           profondeur, orphelines, liens, ancres, cocon par répertoire
 ├─ pagespeed / crux_report / gsc_report / indexnow_submit   si l'accès est dans l'environnement
 ├─ Findings                    un constat par code de règle, URLs agrégées, id stable
 └─ report_markdown + diff_reports + envkeys.redact_obj      écriture masquée des sorties
```

## Modules

| Module | Rôle | Dépendances |
|---|---|---|
| `audit_rules.py` | Catalogue unique des règles : code, priorité, catégorie, étiquette, source, correctif. Contrôles par page et hreflang, partagés avec `generate_report.py` | stdlib |
| `htmlsignals.py` | Parseur HTML : meta, canonical, hreflang, JSON-LD, liens avec leur zone (`main`, `boilerplate`, `unknown`), nombre de mots | stdlib |
| `linkgraph.py` | Graphe des liens internes, sur des dicts simples pour être testable sans réseau | stdlib |
| `sitemaps.py` | Découverte et lecture des sitemaps, contrôles lastmod, sitemap proposé | stdlib |
| `robotstxt.py`, `ai_bots.py` | Interprétation RFC 9309, catalogue des crawlers | stdlib |
| `envkeys.py` | Lecture des secrets (environnement, chemin de fichier), masquage | stdlib |
| `pagespeed.py`, `crux_report.py` | API Google de performance | stdlib |
| `gsc_report.py` | API Search Console (Search Analytics). Dépendances importées à l'appel seulement | `google-auth`, `requests` |
| `report_markdown.py`, `diff_reports.py` | Rendu du rapport et comparaison, fonctions pures du JSON | stdlib |

## Outils autonomes (hors `run_audit.py`)

| Script | Rôle | Dépendances |
|---|---|---|
| `crawler_logs.py` | Journaux serveur : identifie les crawlers (catalogue `ai_bots.py` + moteurs et outils SEO), vérifie leurs IP contre les listes JSON des fournisseurs, produit des constats étiquetés. Les IP ne sortent jamais du processus : compteurs et agrégats /24, /48 | stdlib |
| `glossary_check.py` | Glossaire : `build` (HTML `<dl>` et JSON-LD `DefinedTermSet` depuis les mêmes lignes), `audit` (termes, balisage visible, ancres, occasions de liens sur un échantillon du sitemap), `suggest` (sigles, `<abbr>`, `<dfn>` présents sur plusieurs pages). Réutilise `robotstxt.py` et `sitemaps.py` | stdlib |

| `search_console.py` | Client REST de l'API Search Console au nom du compte de service du propriétaire : sites, sitemaps (liste et `sitemaps.submit`), URL Inspection (catégories tirées des champs énumérés, état local, plafond de quota), Search Analytics. Transport injectable : testé sans réseau | stdlib ; `google-auth` + `requests` seulement pour transformer la clé en jeton |
| `url_discovery.py` | Découverte des nouvelles URL : robots.txt, sitemaps et `lastmod`, différences avec le passage précédent, lien depuis l'accueil, flux et hub WebSub ; avec `--submit` : `sitemaps.submit`, notification WebSub, IndexNow ; avec `--inspect` : inspection. Réutilise `robotstxt.py`, `sitemaps.py`, `search_console.py`, `indexnow_submit.py` | stdlib (+ Search Console comme ci-dessus) |

Ces outils restent séparés de `run_audit.py` : `crawler_logs.py` lit des
fichiers que seul le propriétaire possède, `glossary_check.py` demande un
choix éditorial (quel glossaire, quels termes), `url_discovery.py` et
`search_console.py` agissent au nom du propriétaire et tournent à chaque
publication plutôt qu'à chaque audit.

Flux de `url_discovery.py` :
```
url_discovery.py
 ├─ accueil                     liens <a href>, flux <link rel=alternate>
 ├─ robots.txt                  lignes Sitemap:
 ├─ sitemaps.discover           URL + lastmod ; diff avec discovery_state.json (nouvelles, modifiées, retirées)
 ├─ maillage                    nouvelles URL liées depuis l'accueil ou --hub-page ?
 ├─ flux                        hub WebSub déclaré ? (XML ou en-tête Link)
 ├─ search_console              sitemaps connus ; --submit : sitemaps.submit si changement
 ├─ websub                      --submit : POST hub.mode=publish au hub déclaré
 ├─ indexnow                    --submit : URL changées, fichier de clé vérifié avant
 ├─ inspection                  --inspect N : search_console.run_inspection, nouvelles URL d'abord
 └─ discovery_<date>.md/.json   sorties masquées ; URL « en attente » gardées tant que l'annonce n'a pas réussi
```

## Choix de conception
- **Un constat par code de règle**, URLs agrégées, avec un identifiant
  stable (`sha1(code)`). Le diff compare des identifiants, puis des
  ensembles d'URLs.
- **Priorité portée par la règle**, pas par le script. Une règle CLAIMED
  est P2 (vérifié par un test). Le plan reste ainsi cohérent avec
  [data-hygiene.md](../references/data-hygiene.md).
- **Échantillon déclaré.** Le crawl commence par les URLs du sitemap, pour
  couvrir ce que le site déclare. Le rapport dit si toutes ont été vues
  (`crawl_complete`). Les orphelines ne sont conclusives que dans ce cas.
- **Correctifs sûrs seulement.** Le script ne modifie ni le site ni le
  dépôt. Il produit des artefacts : sitemap proposé, liste IndexNow. Les
  corrections de code passent par la procédure PLAN → FIX → VERIFY, avec le
  GO du propriétaire.
- **Masquage final.** Tout le JSON et tout le Markdown passent par
  `envkeys.redact_obj` / `redact` avant écriture, même si aucun module n'est
  censé y écrire une clé.

## Évaluations
`evals/evals.json` : 8 cas au format du skill-creator d'Anthropic (prompt,
sortie attendue, critères vérifiables). Ils s'appuient sur les fixtures de
`tests/fixtures/` et ne s'exécutent pas seuls.

## Tests
`tests/` contient 91 tests hors ligne. `test_discovery.py` couvre
`search_console.py` et `url_discovery.py` avec des transports simulés :
catégories d'inspection, quotas, reprises sur 5xx, jeton absent des erreurs,
URL encodées de `sitemaps.submit`, notification WebSub, URL en attente
conservées sans `--submit`, clé IndexNow absente des sorties. `test_glossary_logs.py` couvre
`glossary_check.py` et `crawler_logs.py` sur des fixtures (`tests/fixtures/glossary/`,
`tests/fixtures/logs/`), sans réseau. `test_automation.py` sert
`tests/fixtures/site/` sur 127.0.0.1 et lance `run_audit.main()` deux fois.
Les deux passages vérifient les problèmes plantés dans le site de test,
l'écriture du diff et l'absence de la clé IndexNow de test dans toutes les
sorties.
