# Hygiène des données SEO/GEO

Revu le 2026-09-27.

## Étiquettes de preuve

Toute affirmation factuelle de ce skill, et de tout audit qu'il produit,
porte une étiquette et une source datée :

| Étiquette | Signifie | Exemple de source |
|---|---|---|
| **ESTABLISHED** | Documentation officielle ou déclaration du fournisseur sur **son propre** produit | Google Search Central, doc OpenAI des bots, RFC |
| **SUPPORTED** | Étude **indépendante** (ne vend pas la solution étudiée) avec méthode et données publiées | Pew Research, CJR/Tow Center, EBU, Reuters Institute, article académique |
| **CLAIMED** | Affirmation d'un vendeur d'outil ou d'un blog SEO, y compris une étude de vendeur | « +40 % de citations avec le schema X » |

Une étude de vendeur dont la méthode est publiée (Ahrefs, Semrush, SE
Ranking, Seer, SparkToro, Profound, scan Cloudflare) reste **CLAIMED**, avec
la mention « méthode publiée » : elle est utile, vérifiable, mais pas
indépendante.

Règles :
- Un CLAIMED n'est **jamais** présenté comme établi, ni utilisé seul pour
  prioriser un chantier.
- Un fournisseur qui parle de son produit = ESTABLISHED ; le même
  fournisseur qui parle du marché ou des concurrents = CLAIMED.
- Une date seule n'est pas une preuve : il faut l'URL et ce qu'elle dit.
- Registre complet des affirmations et des croyances démenties :
  [evidence.md](evidence.md).

## Baser les décisions sur de la donnée mesurée
Toute priorité (P0/P1/P2) s'appuie sur des données mesurées quand elles
existent : Search Console, Bing Webmaster Tools, analytics, Core Web Vitals
terrain (CrUX), journaux serveur. À défaut, le dire explicitement plutôt que
de généraliser une bonne pratique non vérifiée pour ce site précis.

## Mesuré, inféré, généré
Dans un audit, marquer chaque constat :
- **Mesuré** : source concrète (Search Console, CrUX, requête HTTP datée,
  journal serveur).
- **Inféré** : lecture du HTML public, du code, d'une configuration.
- **Hypothèse / génération IA** : estimation, recommandation générique,
  contenu rédigé par un modèle — à valider avant d'être traité comme un fait.

Risque de boucle : une IA génère une statistique plausible, qui est citée
comme vérifiée, puis reprise par d'autres contenus IA. Le garde-fou du skill
`seo` (« ne jamais inventer une donnée manquante, utiliser `null` ou
`[À VÉRIFIER]` ») s'applique ici aussi.

## Péremption
Les recommandations SEO/GEO se périment (rich results retirés, bots
renommés, politiques CDN). Chaque fichier de `references/` porte sa date de
revue. Avant de ressortir une affirmation datée de plus de 3 mois dans un
audit, la revérifier à sa source primaire. Les chiffres publics utilisés
comme preuve sociale sur un site (« 610+ sites créés ») doivent rester exacts
et datés, sinon ils deviennent un point faible de crédibilité.
