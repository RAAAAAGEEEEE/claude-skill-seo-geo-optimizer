# Hygiène des données SEO/GEO

## Baser les décisions sur de la vraie data mesurée
Toute recommandation de priorité (P0/P1/P2) doit s'appuyer sur des données
mesurées quand elles existent : Search Console (impressions, clics,
position), analytics (trafic, conversions), performance réelle (Core Web
Vitals terrain, pas seulement labo). À défaut de donnée mesurée disponible,
le dire explicitement plutôt que de généraliser à partir de bonnes
pratiques génériques non vérifiées pour ce site précis.

## Ne jamais confondre donnée mesurée et génération IA
Ne pas recycler du contenu généré par une IA (y compris par ce skill) comme
s'il s'agissait d'une donnée vérifiée. Dans un audit ou un rapport, marquer
explicitement chaque affirmation :
- **Mesuré** : source concrète citée (Search Console, analytics, capture
  d'écran, fichier de log, requête `curl`/`WebFetch` datée).
- **Hypothèse / génération IA** : estimation, recommandation générique,
  ou contenu rédigé par un modèle — à valider avant de le traiter comme un
  fait.

Ce risque de "boucle d'apprentissage" (une IA génère une statistique
plausible, qui est ensuite citée comme si elle était vérifiée, puis reprise
par d'autres contenus IA) dégrade la fiabilité de toute la base de
connaissances SEO d'un projet dans le temps. Le garde-fou du skill `SEO`
("ne jamais inventer une donnée manquante, utiliser `null` ou `[À VÉRIFIER]`")
s'applique aussi ici.

## Audit périodique de la base de connaissances
Les recommandations SEO/GEO se périment (algorithmes, seuils Core Web
Vitals, format de schema recommandé, liste des bots IA). Revoir
périodiquement :
- Les fichiers `AUDIT_GEO.md` produits par ce skill — dater chaque
  recommandation, ne pas les traiter comme valides indéfiniment.
- Les stats citées dans [audit-framework.md](audit-framework.md) et
  [ai-crawlers.md](ai-crawlers.md) — si une stat semble ancienne ou
  contestée, la re-vérifier par recherche avant de la ressortir dans un
  nouvel audit.
- Les chiffres publics utilisés comme preuve sociale sur un site (ex. "610+
  sites créés") — s'assurer qu'ils restent exacts et datés, sinon ils
  deviennent un point faible de crédibilité s'ils sont repris dans un actif
  citable (cf. pénalité "donnée invérifiable" du barème `SEO`).
