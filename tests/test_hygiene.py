"""Offline tests for 2.7.0: hygiene_check.py (scanner and preview probes,
log measures without IP output, near-duplicate city pages, byline, bursts).

Run: python -m unittest discover -s tests
"""

import ipaddress
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import hygiene_check as h  # noqa: E402


def fake_request(table):
    """table: {(path, ua_fragment or None): (status, headers, body, error)}."""
    def request(url, ua, timeout=15.0):
        path = "/" + url.split("/", 3)[3] if url.count("/") >= 3 else "/"
        for (p, frag), resp in table.items():
            if p == path and (frag is None or frag in ua):
                return resp
        return 404, {}, "", None
    return request


class Probes(unittest.TestCase):
    def test_closed_scanner_ok_200_flagged_challenge_flagged(self):
        table = {
            ("/", "WhatsApp"): (200, {}, "ok", None),
            ("/", "facebookexternalhit"): (403, {}, "Just a moment...", None),
            ("/", "ClaudeBot"): (403, {"cf-mitigated": "challenge"}, "", None),
            ("/", "OAI-SearchBot"): (429, {}, "", None),
            ("/", None): (200, {}, "ok", None),
            ("/.env", None): (None, {}, "", "closed"),
            ("/.git/config", None): (200, {}, "[core]", None),
            ("/wp-login.php", None): (403, {}, "", None),
        }
        r = h.run_probes("https://example.test", request=fake_request(table), pause=0)
        verdicts = {x["path"]: x["verdict"] for x in r["scanner"]}
        self.assertEqual(verdicts["/.env"], "closed")
        self.assertEqual(verdicts["/.git/config"], "served")
        codes = [(f["code"], f["priority"]) for f in r["findings"]]
        self.assertIn(("scanner-path-served", "P1"), codes)
        self.assertIn(("scanner-path-not-444", "P2"), codes)
        refused = {x["robot"]: x["verdict"] for x in r["preview"]}
        self.assertEqual(refused["WhatsApp"], "ok")
        self.assertEqual(refused["facebookexternalhit"], "challenge")
        self.assertEqual(refused["ClaudeBot"], "challenge")
        self.assertEqual(refused["OAI-SearchBot"], "http-429")
        self.assertEqual(sum(f["code"] == "preview-robot-refused" for f in r["findings"]), 3)

    def test_unreachable_home_concludes_nothing(self):
        r = h.run_probes("https://example.test", request=lambda *a, **k: (None, {}, "", "timeout"), pause=0)
        self.assertFalse(r["reachable"])
        self.assertEqual(r["findings"], [])

    def test_challenge_detection(self):
        self.assertTrue(h.is_challenge(403, {"CF-Mitigated": "challenge"}, ""))
        self.assertTrue(h.is_challenge(403, {}, "<title>Just a moment...</title>"))
        self.assertFalse(h.is_challenge(403, {}, "forbidden"))
        self.assertFalse(h.is_challenge(200, {}, "Just a moment"))


def line(ip, path, status=200, ua="Mozilla/5.0 Chrome/130"):
    return f'{ip} - - [04/Nov/2026:10:00:00 +0000] "GET {path} HTTP/1.1" {status} 100 "-" "{ua}"'


class Logs(unittest.TestCase):
    def test_measures_and_no_ip_in_findings(self):
        lines = (
            [line("172.67.1.1", "/", ua="Mozilla/5.0 Chrome/130")] * 30      # Cloudflare as client
            + [line("203.0.113.5", "/.env", 444)] * 10                       # scanner
            + [line("203.0.113.6", "/wp-login.php", 444)] * 5
            + [line("10.9.9.9", "/", ua="Mozilla/5.0 HeadlessChrome/151")] * 20  # internal + headless
            + [line("198.51.100.7", "/page")] * 35
        )
        nets = [ipaddress.ip_network("172.64.0.0/13")]
        r = h.analyze_logs(lines, internal_ips=["10.9.9.9"], cf_nets=nets)
        self.assertEqual(r["lines"], 100)
        self.assertEqual(r["scanner"], 15)
        self.assertEqual(r["scanner_distinct_sources"], 2)
        self.assertEqual(r["cloudflare_as_client"], 30)
        self.assertEqual(r["internal"], 20)
        self.assertEqual(r["headless"], 20)
        self.assertEqual(r["status_444"], 15)
        fnd = h.log_findings(r)
        codes = {f["code"]: f["priority"] for f in fnd}
        self.assertEqual(codes["real-ip-missing"], "P1")
        self.assertEqual(codes["internal-traffic"], "P1")
        self.assertEqual(codes["scanner-noise"], "P2")
        text = " ".join(f["message"] for f in fnd)
        for ip in ("203.0.113", "172.67.1.1", "10.9.9.9", "198.51.100"):
            self.assertNotIn(ip, text)

    def test_without_ranges_or_internal_ips_says_not_measured(self):
        r = h.analyze_logs([line("198.51.100.7", "/")] * 10)
        codes = {f["code"] for f in h.log_findings(r)}
        self.assertIn("cf-ranges-not-loaded", codes)
        self.assertIn("internal-ip-not-given", codes)
        self.assertNotIn("real-ip-missing", codes)


CITY = ("<html><head><title>Plombier {c}</title></head><body><nav>menu accueil contact</nav><main><h1>Plombier à {c}</h1>"
        "<p>Notre entreprise intervient rapidement pour tous vos dépannages de plomberie, fuite d'eau, chauffe-eau, "
        "débouchage de canalisation, installation de sanitaires et rénovation complète de salle de bains avec devis "
        "gratuit et garantie sur toutes nos interventions réalisées par des artisans qualifiés et assurés pour votre "
        "tranquillité et votre confort au quotidien dans {c} et ses environs proches de la ville.</p>"
        "</main><footer>mentions</footer></body></html>")
ARTICLE = ("<html><head><title>Guide</title></head><body><main><h1>Guide</h1><p class=\"byline\">Par Jeanne Martin</p><p>"
           + "contenu original issu d'un chantier réel avec mesures prises sur place " * 40 + "</p></main></body></html>")
ARTICLE_ANON = ARTICLE.replace('class="byline"', "").replace("Par Jeanne Martin", "")


class Content(unittest.TestCase):
    def test_city_pages_flagged_as_duplicates(self):
        cities = ["lyon", "paris", "nantes", "lille", "tours", "metz"]
        pages = {f"https://x.test/plombier/{c}": h.parse_content(CITY.format(c=c.capitalize())) for c in cities}
        fnd = h.analyze_content(pages, {u: None for u in pages})
        self.assertIn("near-duplicate-pages", {f["code"] for f in fnd})

    def test_distinct_pages_not_flagged(self):
        pages = {}
        for i in range(6):
            page = h.parse_content(ARTICLE)
            page["words"] = [f"mot{i}_{j}" for j in range(400)]
            pages[f"https://x.test/guides/p{i}"] = page
        fnd = h.analyze_content(pages, {u: None for u in pages})
        self.assertNotIn("near-duplicate-pages", {f["code"] for f in fnd})

    def test_byline_detection_and_finding(self):
        self.assertTrue(h.parse_content(ARTICLE)["byline"])
        self.assertFalse(h.parse_content(ARTICLE_ANON)["byline"])
        ld = '<script type="application/ld+json">{"@type":"Article","author":{"@type":"Person","name":"A"}}</script>'
        self.assertTrue(h.parse_content(ARTICLE_ANON.replace("</head>", ld + "</head>"))["byline"])
        fnd = h.analyze_content({"https://x.test/blog/a": h.parse_content(ARTICLE_ANON)}, {})
        self.assertIn("no-byline", {f["code"] for f in fnd})
        fnd = h.analyze_content({"https://x.test/blog/a": h.parse_content(ARTICLE)}, {})
        self.assertNotIn("no-byline", {f["code"] for f in fnd})

    def test_publication_burst(self):
        urls = {f"https://x.test/p/{i}": "2026-11-03T10:00:00Z" for i in range(30)}
        urls.update({f"https://x.test/q/{i}": f"2026-10-{i + 1:02d}" for i in range(5)})
        fnd = h.analyze_content({}, urls)
        self.assertIn("publication-burst", {f["code"] for f in fnd})

    def test_menu_and_footer_excluded_from_text(self):
        words = h.parse_content(CITY.format(c="Lyon"))["words"]
        self.assertNotIn("menu", words)
        self.assertNotIn("mentions", words)


if __name__ == "__main__":
    unittest.main()
