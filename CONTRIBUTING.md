# Contribuer

Merci de votre intérêt. Issues et pull requests sont bienvenues.

## Avant d'ouvrir une pull request
1. `python -m unittest discover -s tests` doit passer. À la version 2.3.2,
   66 tests hors ligne passent.
2. Tout script ajouté ou modifié a un test dans `tests/`. Si le script fait
   du réseau, le tester sur le site de test local (`tests/fixtures/site/`,
   servi en 127.0.0.1) ou avec un appel simulé, jamais contre un site tiers.
3. Toute nouvelle règle d'audit va dans `scripts/audit_rules.py`, avec :
   - une priorité ;
   - une étiquette ESTABLISHED / SUPPORTED / CLAIMED ;
   - une source ;
   - un correctif.

   Une règle CLAIMED reste en P2 (un test le vérifie).
4. Toute affirmation ajoutée dans `references/` porte une source primaire
   datée et son étiquette ([data-hygiene.md](references/data-hygiene.md)).
   Une méthode de praticien sans données est CLAIMED. En cas de conflit avec
   la documentation de Google, c'est Google qui prime.
5. La documentation est mise à jour **dans le même commit** que le code :
   - `SKILL.md` si la procédure change ;
   - `docs/` et `.env.example` pour une nouvelle variable ;
   - `CHANGELOG.md` dans tous les cas.
6. Aucun secret, aucune donnée personnelle, aucun rapport d'audit réel dans
   le dépôt. `seo-reports/` et `*.env` sont ignorés par git.

## Style
- Python 3.10+, bibliothèque standard autant que possible. Toute dépendance
  tierce est optionnelle et chargée à la demande (voir Search Console).
- Messages destinés à l'utilisateur en français. Commentaires et noms en
  anglais ou en français, sans mélange dans un même fichier.
- Toute commande documentée doit avoir été exécutée.

## Signaler une faille
Voir [SECURITY.md](SECURITY.md).
