# Indexation — ce qui est autorisé, ce qui est interdit

## Google : sitemap + Search Console, rien d'autre
`sitemap.xml` à jour, référencé dans `robots.txt`, soumis dans Search
Console. Inspection d'URL manuelle et ponctuelle pour une page importante qui
tarde à être crawlée. C'est le mécanisme normal et il n'y a rien d'autre à
construire.

### Interdit — Google Indexing API hors périmètre
Cette API est réservée par Google à `JobPosting` et à `BroadcastEvent`
intégré dans une `VideoObject`. L'utiliser pour des pages marketing, des
articles ou des pages produit est un usage détourné des conditions
d'utilisation, avec un risque documenté de coupure d'accès à l'API pour le
compte concerné.

Si l'utilisateur demande « indexer plus vite via l'API Google » pour un type
de page hors de ce périmètre : expliquer la restriction, proposer sitemap +
Search Console, et IndexNow pour les autres moteurs.

### Interdit — auto-submit maison
Ne pas coder de mécanisme qui pousse des URLs vers un moteur en dehors du
flux sitemap → crawl (ping répétés, soumissions en boucle). Ça n'accélère
rien de façon fiable et s'apparente à du spam d'indexation.

## Bing, Yandex, Naver, Seznam, Yep : IndexNow
IndexNow est le mécanisme **prévu, gratuit et explicitement encouragé** par
ces moteurs pour signaler une URL nouvelle ou modifiée. Rien à voir avec un
détournement d'API : c'est son usage nominal.

- Google **n'y participe pas** (position confirmée en 2026) — ne jamais
  présenter IndexNow comme un moyen d'accélérer l'indexation Google.
- Pas de quota documenté côté IndexNow (contrairement à l'API URL Submission
  de Bing, limitée à 10 000 URLs/jour/domaine, que Microsoft pousse à
  abandonner au profit d'IndexNow).
- Cloudflare propose une intégration native en un clic sur les plans payants.
- Script : [`../scripts/indexnow_submit.py`](../scripts/indexnow_submit.py)
  — vérifie que le fichier de clé est publiquement accessible **avant** toute
  soumission, et refuse de soumettre sinon.

Mise en place (une fois par site) :
1. Générer une clé : `python -c "import uuid; print(uuid.uuid4().hex)"`
2. Publier `https://example.com/<clé>.txt` contenant uniquement la clé.
3. `python scripts/indexnow_submit.py --host example.com --key <clé> --urls urls.txt --dry-run`
   puis sans `--dry-run` une fois la vérification passée.

Bon usage : soumettre les URLs **nouvelles ou réellement modifiées**, pas
l'intégralité du sitemap à chaque exécution.

## Brave Search
Soumission manuelle et ponctuelle sur `https://search.brave.com/submit-url`
— pertinent pour la visibilité dans le web search de Claude, voir
[ai-crawlers.md](ai-crawlers.md#geo--soumission-brave-search). Ne pas
automatiser en masse.

## Rappel : l'indexation n'est pas le problème le plus fréquent
Avant de chercher à accélérer l'indexation, vérifier que le site est
réellement accessible aux crawlers ([cloudflare-ai-access.md](cloudflare-ai-access.md))
et que les pages concernées ne sont pas exclues par un `noindex`, un
canonical mal orienté ou une redirection. Un problème d'accès ne se corrige
pas en soumettant plus fort.
