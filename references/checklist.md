# Checklist — uniquement ce que les scripts ne peuvent PAS vérifier

**Principe d'élagage : tout ce qui est automatisable a été retiré de cette
checklist.** Ne pas re-vérifier à la main ce que `generate_report.py`
contrôle déjà (HTTP, title, meta description, canonical, H1, JSON-LD valide,
robots.txt/sitemap, impressions Search Console) ni ce que
`check_ai_access.py` contrôle (accès réel des crawlers IA).

Cette liste ne contient que ce qui exige un jugement humain ou une donnée
externe au HTML.

## Avant de commencer
- [ ] `python scripts/check_ai_access.py <url>` exécuté — **si des bots de
      recherche sont bloqués, traiter ça avant tout le reste**, le reste a un
      plafond de zéro côté GEO.
- [ ] `python scripts/generate_report.py --urls urls.txt --out-prefix audit`
      exécuté — le rapport sert de base, cette checklist le complète.

## Jugement éditorial (non automatisable)
- [ ] Le title est-il *cliquable*, pas seulement présent et bien dimensionné ?
- [ ] La meta description donne-t-elle une raison de cliquer, ou décrit-elle
      platement la page ?
- [ ] Chaque section commence-t-elle par une réponse directe (retrieval IA),
      ou par du contexte/préambule ?
- [ ] Le contenu apporte-t-il quelque chose que les concurrents n'ont pas
      (donnée propriétaire, expérience réelle, chiffre daté) ?
- [ ] Cannibalisation : deux pages ciblent-elles la même intention ?
- [ ] Contenu obsolète non rafraîchi depuis > 12 mois sur des sujets qui
      bougent ?

## Signaux de confiance (vérification manuelle)
- [ ] Page À-propos réelle, pas un paragraphe générique.
- [ ] Mentions légales complètes : éditeur, hébergeur, numéro
      d'immatriculation si applicable, contact.
- [ ] Auteur identifiable sur le contenu éditorial (`Person` plutôt
      qu'`Organization` quand une vraie personne écrit).
- [ ] NAP (nom/adresse/téléphone) cohérent entre le site, Google Business
      Profile et les annuaires — en commerce local.
- [ ] Date de dernière mise à jour visible sur le contenu daté.
- [ ] Chiffres publics utilisés comme preuve sociale : datés et exacts ?

## Données externes (accès requis)
- [ ] Search Console : pages en impressions sans clic → problème de
      title/description, pas de contenu (`gsc_report.py`).
- [ ] Search Console : pages attendues avec zéro impression → problème
      d'indexation, pas de ranking.
- [ ] CrUX : Core Web Vitals terrain (`crux_report.py`). Pas de données =
      trafic insuffisant, **pas** un problème de performance.
- [ ] Bing/Yandex : URLs récentes soumises via IndexNow
      (`indexnow_submit.py`) ?

## Décisions à remonter à l'utilisateur (ne jamais trancher seul)
- [ ] Blocage/déblocage des crawlers IA (arbitrage contenu ouvert vs
      monétisation).
- [ ] Migration d'URLs, sous-domaine vs sous-répertoire.
- [ ] Suppression ou désindexation de pages existantes.
