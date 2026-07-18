# Checklist audit SEO/GEO (pass rapide — remplir dans AUDIT_GEO.md)

Pour le détail technique/on-page/E-E-A-T, voir [audit-framework.md](audit-framework.md).

## Technique
- [ ] `<title>` unique et descriptif par page (50-60 car., mot-clé proche du début)
- [ ] meta description par page (150-160 car., CTA inclus)
- [ ] Un seul H1 par page, hiérarchie Hn logique
- [ ] URLs propres, lisibles, sans paramètres inutiles
- [ ] `sitemap.xml` présent + à jour + référencé dans `robots.txt`
- [ ] Core Web Vitals : LCP < 2.5s, INP < 200ms, CLS < 0.1
- [ ] HTTPS actif partout, pas de mixed content
- [ ] Balises canonical correctes (pas de duplicate content)

## Schema JSON-LD
- [ ] JSON-LD présent (pas Microdata/RDFa)
- [ ] Schema **valide** (champs requis présents) — tester chaque bloc avec
      `scripts/validate_schema.py` ou le Rich Results Test
- [ ] `Organization` + `sameAs` sur la home
- [ ] Type spécifique par page (`LocalBusiness`/sous-type, `Product`, `Article`...)
- [ ] `FAQPage` là où il y a des Q/R
- [ ] `AggregateRating` si avis disponibles
- [ ] `BreadcrumbList` sur les pages internes
- [ ] `dateModified` à jour sur le contenu éditorial

## Crawlers IA
- [ ] `robots.txt` : décision explicite (pas par défaut) sur GPTBot, ClaudeBot,
      PerplexityBot, Google-Extended, OAI-SearchBot, Claude-SearchBot,
      Applebot-Extended — voir [ai-crawlers.md](ai-crawlers.md)
- [ ] `llms.txt` présent à la racine (description + pages clés)
- [ ] Pas de contenu clé bloqué au JS/derrière login pour les crawlers

## Contenu / retrieval IA
- [ ] TL;DR / réponse directe en tête de section (44% des citations LLM
      viennent du premier tiers de la page)
- [ ] FAQ en vrai balisage Q→R
- [ ] Contenu factuel, chiffré, daté, sourcé (citer des sources tierces
      augmente la probabilité de citation par les IA génératives)

## E-E-A-T
- [ ] Page À-propos réelle
- [ ] Mentions légales (éditeur, hébergeur, SIRET si applicable)
- [ ] Bio auteur / équipe
- [ ] NAP (Name/Address/Phone) cohérent partout pour le local
- [ ] Timestamp "dernière mise à jour" visible + `dateModified` schema
