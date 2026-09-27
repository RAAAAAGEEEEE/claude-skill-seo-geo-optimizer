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
| `gsc_report.py` | API Search Console | `google-auth`, `requests` |
| `report_markdown.py`, `diff_reports.py` | Rendu du rapport et comparaison, fonctions pures du JSON | stdlib |

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

## Tests
`tests/` contient 52 tests hors ligne. `test_automation.py` sert
`tests/fixtures/site/` sur 127.0.0.1 et lance `run_audit.main()` deux fois.
Les deux passages vérifient les problèmes plantés dans le site de test,
l'écriture du diff et l'absence de la clé IndexNow de test dans toutes les
sorties.
