# Confiance et hygiène du site (ajouté le 2026-11-05, v2.8.0)

Origine : rapports RoastMyUrl du 2026-11-04 (vuntum.com id 13426, siteservi.com id 13469). Ces contrôles sont
**P2 au plus et ne sont pas des facteurs de classement**. Ils sont là parce qu'un site propre se vérifie en
une commande, pas parce qu'ils font monter dans Google ou dans les réponses IA. Un score RoastMyUrl n'est pas
un score de visibilité : sa note globale mélange réseau, DNS, e-mail, vie privée, souveraineté.

## Ce qui est mesuré (`scripts/trust_check.py`, étape `trust` de `run_audit.py`)

| Code | Contrôle | Effet sur classement ou citation IA | Source (relue le 2026-11-05) | Étiquette |
|---|---|---|---|---|
| `http-no-redirect` | `http://` redirige en 301 vers `https://` | Faible : Google « utilise HTTPS comme indicateur positif de qualité » | web.dev, Enable HTTPS (non datée) | ESTABLISHED |
| `hsts-missing` | `Strict-Transport-Security` max-age >= 180 jours | Aucun. Évite une redirection et le rétrogradage ; pas de lien avec le classement | web.dev, Enable HTTPS | ESTABLISHED |
| `security-headers-missing` | `X-Content-Type-Options: nosniff`, `Referrer-Policy` | Aucun | MDN, guide des en-têtes HTTP | CLAIMED (pour tout effet SEO) |
| `security-txt-missing` / `-expired` | `/.well-known/security.txt` avec Contact et Expires | Aucun : contact de sécurité | RFC 9116 | ESTABLISHED (format) |
| `org-sameas-missing` | `sameAs` sur l'Organization de l'accueil (profils réels seulement) | Désambiguïsation de l'entité, soutenu par la doc Google | Google, schéma Organization (non datée) | ESTABLISHED (supporté par la doc), effet citation IA non démontré |
| `org-contact-missing` | email, téléphone ou `contactPoint` dans le schéma, identiques au texte visible | Idem, plus confiance pour l'utilisateur | Google, schéma Organization | ESTABLISHED |
| `sitemap-lastmod-mismatch` | `lastmod` du sitemap proche du `dateModified` annoncé par la page (tolérance 2 jours) | Réel : Google utilise `lastmod` pour planifier l'exploration et finit par l'ignorer s'il ne correspond pas à la réalité | Google Search Central, 2023-06-26 | ESTABLISHED |

Page Google « page experience » : seuls les Core Web Vitals sont utilisés par les systèmes de classement ;
les autres aspects (dont le service sécurisé) n'aident pas directement à monter (relue le 2026-11-05).

## Écartés (cosmétiques ou sans effet démontré)
- **ai.txt** : aucun fournisseur ne s'engage à le lire (même statut que llms.txt, voir licensing-signals.md).
- **HSTS preload, includeSubDomains** : engage tous les sous-domaines, irréversible en pratique. Jamais par défaut.
- **SRI** : impossible pour Google Fonts (CSS dynamique) et Google Tag Manager (script mouvant).
- **CAA, DNSSEC, Certificate Transparency, Qualys, ports, WAF, géolocalisation, souveraineté** : infrastructure,
  aucun lien avec la visibilité.
- **CSP complète** : casse GTM, scripts en ligne, iframes. Seulement en Report-Only, sur décision du propriétaire.
- **SPF, DKIM, DMARC** : délivrabilité des e-mails du propriétaire, hors SEO/GEO. À signaler au propriétaire si
  le site envoie des mails, ne pas coder dans ce skill.
- **« Liens réseaux sociaux », « Prêt pour les agents », numéro de téléphone, CGU** : ne créer aucun profil ni
  numéro pour passer un contrôle. `sameAs` seulement avec des profils qui existent déjà.
- **Conseil « +41 % citations, +33 % statistiques »** : tiré de l'étude GEO (arXiv 2311.09735, KDD 2024), mesurée
  sur un moteur de test ; CLAIMED pour les moteurs réels.

## Correction (lots, un diff à la fois, accord du propriétaire pour la production)
1. **nginx** : snippet unique inclus dans les `location /` : `add_header Strict-Transport-Security "max-age=31536000" always;`,
   `X-Content-Type-Options nosniff`, `Referrer-Policy strict-origin-when-cross-origin`, `X-Frame-Options SAMEORIGIN`.
   Sauvegarde horodatée avant, `nginx -t`, recharge, puis `curl -I` **par le CDN** (Cloudflare peut surcharger).
   Un `add_header` dans un bloc `location` supprime ceux du bloc parent : inclure le snippet partout où il en existe.
2. **http vers https derrière Cloudflare** : réglage « Always Use HTTPS » (tableau de bord, à lister au propriétaire),
   ou règle de redirection ; ne pas le faire côté origine si Cloudflare est en mode flexible (boucle).
3. **security.txt** : `Contact: mailto:<adresse réelle>`, `Expires:` au plus un an, `Preferred-Languages: fr, en`.
   Penser à la date de renouvellement dans le planning.
4. **sameAs** : profils officiels existants uniquement ; sinon ne rien écrire.
5. **lastmod qui suit le vrai changement** : `lastmod` = date du dernier commit qui touche le fichier de la page
   (`git log -1 --format=%cs -- <fichier>`), `dateModified` du schéma = la même valeur, jamais la date du rendu.
   Un cron de génération quotidien ne doit pas réécrire les dates. Vérifier ensuite qu'il ne reste pas de pic de
   dates identiques (`sitemap-lastmod-uniform`).
