# Installation

Retour : [README](../README.md) · Suite : [USAGE](USAGE.md),
[CONFIGURATION](CONFIGURATION.md).

## Prérequis
- Python 3.10 ou plus récent. Vérifié avec 3.11.15 le 2026-09-28.
- Aucune bibliothèque tierce, sauf pour Search Console :
  `pip install google-auth requests`.
- Bash et curl, seulement pour `audit_site.sh` et `check_backlinks.sh`.

## Installation personnelle (tous les projets)
```bash
git clone https://github.com/RAAAAAGEEEEE/claude-skill-seo-geo-optimizer.git ~/.claude/skills/seo-geo-optimizer
```

## Installation par projet
Copier ou cloner le dossier dans `.claude/skills/seo-geo-optimizer/` à la
racine du projet. Claude Code déclenche le skill sur une demande d'audit
SEO/GEO, de maillage ou de planification d'audit.

## Vérifier l'installation
Depuis le dossier du skill :
```bash
python -m unittest discover -s tests
```
Résultat attendu : `Ran 52 tests` puis `OK`. Aucune requête ne sort de la
machine : le test de bout en bout sert un site de test sur 127.0.0.1.

Vérification faite le 2026-09-28 dans un environnement propre :
1. copie du dépôt sans `.git` ni caches dans un dossier temporaire ;
2. environnement virtuel neuf (`python -m venv`), sans `google-auth`.

Résultat : 52 tests OK. Le module Search Console se déclare `skipped`
quand ses dépendances manquent.

## Mise à jour
```bash
cd ~/.claude/skills/seo-geo-optimizer && git pull
```
Lire [CHANGELOG.md](../CHANGELOG.md) : les ruptures y sont signalées.
