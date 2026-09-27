"""Offline tests for the 2.1.0 automation: link extraction, sitemaps,
internal-linking graph, rules catalogue, secrets handling, PageSpeed parsing,
report diff, and run_audit.py end to end against a fixture site served on
127.0.0.1 (no request leaves the machine).

Run: python -m unittest discover -s tests
"""

import contextlib
import functools
import gzip
import http.server
import io
import json
import os
import re
import sys
import tempfile
import threading
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_rules  # noqa: E402
import diff_reports  # noqa: E402
import envkeys  # noqa: E402
import htmlsignals  # noqa: E402
import linkgraph  # noqa: E402
import pagespeed  # noqa: E402
import report_markdown  # noqa: E402
import run_audit  # noqa: E402
import sitemaps  # noqa: E402


def _parse(html: str, url: str = "https://e.com/a/b") -> htmlsignals.PageSignals:
    return htmlsignals.parse_html(htmlsignals.PageSignals(url=url, final_url=url), html)


class LinkExtraction(unittest.TestCase):
    HTML = ('<html lang="fr"><body><header><a href="/">Accueil</a><nav><a href="/x">X</a></nav></header>'
            '<main><article><header><a href="/a">Parent</a></header><p>Un texte <a href="/a/c#f">voir <b>la</b> page C</a> '
            '<a href="javascript:void(0)">js</a> <a>sans href</a> <a href="#haut">haut</a>'
            '<a href="/img"><img src="i.png" alt="Logo robot"></a></p></article></main>'
            '<footer><a href="/mentions">Mentions</a></footer><script>var s="<a href=\'/zz\'>x</a>";</script></body></html>')

    def test_zones_and_article_header_counts_as_content(self):
        zones = {a["text"]: a["zone"] for a in _parse(self.HTML).anchors}
        self.assertEqual(zones["Accueil"], "boilerplate")
        self.assertEqual(zones["X"], "boilerplate")
        self.assertEqual(zones["Parent"], "main")  # <header> inside <article>
        self.assertEqual(zones["Mentions"], "boilerplate")

    def test_hrefs_resolved_fragment_stripped_and_non_links_kept_as_none(self):
        by_text = {a["text"]: a for a in _parse(self.HTML).anchors}
        self.assertEqual(by_text["voir la page C"]["href"], "https://e.com/a/c")
        self.assertIsNone(by_text["js"]["href"])
        self.assertIsNone(by_text["sans href"]["href"])
        self.assertIsNone(by_text["haut"]["href"])
        self.assertEqual(by_text["Logo robot"]["href"], "https://e.com/img")  # image alt = anchor text
        self.assertNotIn("x", by_text)  # markup inside <script> is not a link

    def test_word_counts(self):
        s = _parse("<body><nav>un deux</nav><main>trois quatre cinq</main><script>six sept</script></body>")
        self.assertEqual(s.word_count, 5)
        self.assertEqual(s.main_word_count, 3)
        self.assertIsNone(_parse("<body><p>a b</p></body>").main_word_count)


class Sitemaps(unittest.TestCase):
    INDEX = (b'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
             b'<sitemap><loc>https://e.com/s1.xml.gz</loc></sitemap></sitemapindex>')
    URLSET = (b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              b'<url><loc>https://e.com/a</loc><lastmod>2026-09-01</lastmod></url>'
              b'<url><loc>https://other.com/b</loc></url></urlset>')

    def test_index_gzip_and_foreign_host(self):
        files = {"https://e.com/sitemap.xml": self.INDEX, "https://e.com/s1.xml.gz": gzip.compress(self.URLSET)}
        result = sitemaps.discover("https://e.com", [], fetch=lambda u, t: (200, files[u], None))
        self.assertEqual(result.urls, ["https://e.com/a", "https://other.com/b"])
        self.assertEqual(result.lastmod_of("https://e.com/a"), "2026-09-01")
        self.assertEqual(sitemaps.foreign_entries(result, "e.com"), ["https://other.com/b"])

    def test_unreadable_sitemap_is_recorded_not_raised(self):
        result = sitemaps.discover("https://e.com", ["https://e.com/bad.xml"], fetch=lambda u, t: (200, b"<nope", None))
        self.assertEqual(result.entries, [])
        self.assertIn("XML illisible", result.read[0]["error"])

    def test_uniform_and_future_lastmod(self):
        s = sitemaps.SitemapSet(entries=[sitemaps.SitemapEntry(f"https://e.com/{i}", "2026-09-27", "s") for i in range(5)])
        self.assertTrue(sitemaps.lastmod_findings(s)["uniform"])
        s.entries.append(sitemaps.SitemapEntry("https://e.com/f", "2099-01-01", "s"))
        lm = sitemaps.lastmod_findings(s)
        self.assertFalse(lm["uniform"])
        self.assertEqual(lm["future"], ["https://e.com/f"])


def _a(href, text="texte", zone="main", rel=""):
    return {"href": href, "raw_href": href, "text": text, "zone": zone, "rel": rel}


class LinkGraph(unittest.TestCase):
    def _graph(self, **kw):
        pages = {
            "https://e.com/": {"status": 200, "indexable": True, "anchors": [
                _a("https://e.com/docs", "Docs", "boilerplate"), _a("https://e.com/old", "cliquez ici"),
                _a("https://e.com/moved", "Déplacée"), {"href": None, "raw_href": "#top", "text": "haut", "zone": "main", "rel": ""},
                {"href": None, "raw_href": None, "text": "bouton", "zone": "main", "rel": ""}]},
            "https://e.com/docs": {"status": 200, "indexable": True, "anchors": [_a("https://e.com/docs/one", "Guide un")]},
            "https://e.com/docs/one": {"status": 200, "indexable": True, "anchors": [
                _a("https://e.com/docs", "la documentation"), _a("https://e.com/docs/two", "guide deux")]},
            "https://e.com/docs/two": {"status": 200, "indexable": True, "anchors": []},
            "https://e.com/lonely": {"status": 200, "indexable": True, "anchors": [_a("https://e.com/")]},
            "https://e.com/old": {"status": 404, "indexable": False, "anchors": []},
            "https://e.com/new": {"status": 200, "indexable": True, "anchors": []},
        }
        resolve = {"https://e.com/moved": "https://e.com/new"}
        return linkgraph.analyze(pages, resolve, "https://e.com/", "e.com",
                                 ["https://e.com/", "https://e.com/docs", "https://e.com/lonely"], complete=True, **kw)

    def test_depth_orphans_broken_and_redirects(self):
        g = self._graph()
        self.assertEqual(g["per_page"]["https://e.com/docs/two"]["depth"], 3)
        self.assertEqual(g["orphans"], ["https://e.com/lonely"])
        self.assertEqual([b["target"] for b in g["broken"]], ["https://e.com/old"])
        self.assertEqual(g["to_redirect"][0]["final"], "https://e.com/new")
        self.assertEqual(g["deep"], [])
        self.assertEqual([d["url"] for d in self._graph(max_depth=2)["deep"]], ["https://e.com/docs/two"])

    def test_anchor_checks_ignore_fragment_links(self):
        g = self._graph()
        self.assertEqual([x["text"] for x in g["generic_anchors"]], ["cliquez ici"])
        self.assertEqual(g["non_crawlable"], {"https://e.com/": 1})  # "#top" is not counted, the href-less <a> is

    def test_contextual_links_and_cocoon(self):
        g = self._graph()
        # /docs is linked from the home navigation AND from the text of /docs/one: it has a contextual inlink.
        self.assertNotIn("https://e.com/docs", g["no_contextual_inlink"])
        self.assertEqual(g["per_page"]["https://e.com/docs"]["inlinks_in_text"], 1)
        self.assertIn("https://e.com/docs/two", g["no_contextual_outlink"])
        cluster = {c["cluster"]: c for c in g["clusters"]}["/docs"]
        self.assertEqual(cluster["children"], 2)
        self.assertEqual(cluster["children_linking_mother"], 1)
        self.assertEqual(g["cocoon_no_uplink"], ["https://e.com/docs/two"])

    def test_no_landmarks_disables_contextual_checks(self):
        pages = {"https://e.com/": {"status": 200, "anchors": [_a("https://e.com/a", zone="unknown")]},
                 "https://e.com/a": {"status": 200, "anchors": []}}
        g = linkgraph.analyze(pages, {}, "https://e.com/", "e.com", [], complete=True)
        self.assertFalse(g["zone_known"])
        self.assertEqual(g["no_contextual_outlink"], [])

    def test_repeated_exact_anchor(self):
        pages = {f"https://e.com/p{i}": {"status": 200, "anchors": [_a("https://e.com/t", "robot humanoïde")]}
                 for i in range(5)}
        pages["https://e.com/t"] = {"status": 200, "anchors": []}
        g = linkgraph.analyze(pages, {}, "https://e.com/p0", "e.com", [], complete=True)
        self.assertEqual(g["repeated_anchors"][0]["anchor"], "robot humanoïde")

    def test_cluster_skips_locale_segment(self):
        self.assertEqual(linkgraph.cluster_of("https://e.com/fr/robots/g1"), ("/fr/robots", "/fr/robots"))
        self.assertIsNone(linkgraph.cluster_of("https://e.com/fr"))


class RulesCatalogue(unittest.TestCase):
    def test_every_code_used_by_the_scripts_exists(self):
        source = "".join((SCRIPTS / f).read_text(encoding="utf-8") for f in ("run_audit.py", "audit_rules.py"))
        used = set(re.findall(r'(?:findings\.add|add)\("([a-z0-9-]+)"', source))
        used |= set(re.findall(r'code = "([a-z0-9-]+)"', source))
        used -= {"canonical-elsewhere", "data-nosnippet", "schema-warning"}  # notes, not findings
        self.assertTrue(used)
        self.assertEqual(sorted(used - set(audit_rules.RULES)), [])

    def test_claimed_rule_never_drives_p0_or_p1(self):
        for code, rule in audit_rules.RULES.items():
            self.assertIn(rule.label, ("ESTABLISHED", "SUPPORTED", "CLAIMED"), code)
            if rule.label == "CLAIMED":
                self.assertEqual(rule.priority, "P2", code)

    def test_finding_id_is_stable(self):
        self.assertEqual(audit_rules.finding_id("orphan-page"), audit_rules.finding_id("orphan-page"))
        self.assertNotEqual(audit_rules.finding_id("orphan-page"), audit_rules.finding_id("deep-page"))


class Secrets(unittest.TestCase):
    def test_redact_nested(self):
        data = {"a": ["https://x/?key=SECRET123", ("SECRET123",)], "b": 3}
        self.assertNotIn("SECRET123", json.dumps(envkeys.redact_obj(data, ["SECRET123", None])))

    def test_secret_reads_env_and_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "creds.json"
            f.write_text("{}", encoding="utf-8")
            with mock.patch.dict(os.environ, {"X_KEY": " k1 ", "X_FILE": str(f), "X_MISSING": str(f) + ".no"}):
                self.assertEqual(envkeys.secret("X_KEY"), "k1")
                self.assertEqual(envkeys.secret_file("X_FILE"), f)
                self.assertIsNone(envkeys.secret_file("X_MISSING"))
                self.assertIsNone(envkeys.secret("X_ABSENT"))


class PageSpeed(unittest.TestCase):
    def test_extract_lab_and_field(self):
        r = pagespeed.extract(json.loads((HERE / "fixtures" / "psi_sample.json").read_text(encoding="utf-8")))
        self.assertEqual(r["performance_score"], 42)
        field = {m["label"]: m for m in r["field_page"]["metrics"]}
        self.assertEqual(field["LCP"]["rating"], "MAUVAIS")
        self.assertAlmostEqual(field["CLS"]["p75"], 0.12)
        self.assertIsNone(r["field_origin"])

    def test_http_error_never_exposes_the_key(self):
        body = io.BytesIO(b'{"error":{"message":"API key not valid for key=SECRETKEY42"}}')
        err = urllib.error.HTTPError("https://x", 400, "Bad Request", {}, body)
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(RuntimeError) as ctx:
                pagespeed.run("https://e.com/", "SECRETKEY42")
        self.assertNotIn("SECRETKEY42", str(ctx.exception))
        self.assertIn("PSI HTTP 400", str(ctx.exception))


class Diff(unittest.TestCase):
    def _report(self, findings, when):
        return {"finished_at": when, "home": "https://e.com/", "summary": {"findings": {"P0": 0, "P1": 0, "P2": 0}},
                "findings": findings}

    def test_new_resolved_changed(self):
        f = lambda code, prio, urls: {"id": audit_rules.finding_id(code), "code": code, "priority": prio,  # noqa: E731
                                      "title": code, "urls": urls, "count": len(urls)}
        old = self._report([f("orphan-page", "P1", ["u1"]), f("thin-page", "P2", ["u2"])], "2026-09-01T00:00")
        new = self._report([f("orphan-page", "P1", ["u1", "u3"]), f("crawler-blocked", "P0", [])], "2026-09-08T00:00")
        d = diff_reports.diff(old, new)
        self.assertEqual([x["code"] for x in d["new"]], ["crawler-blocked"])
        self.assertEqual([x["code"] for x in d["resolved"]], ["thin-page"])
        self.assertEqual(d["changed"][0]["urls_added"], ["u3"])
        self.assertIn("Nouveaux constats (1)", diff_reports.render(d))


class _FixtureHandler(http.server.SimpleHTTPRequestHandler):
    origin = ""

    def log_message(self, *args):  # keep test output clean
        pass

    def do_GET(self):  # noqa: N802
        if self.path in ("/robots.txt", "/sitemap.xml"):
            body = (HERE / "fixtures" / "site" / self.path.lstrip("/")).read_text(encoding="utf-8")
            data = body.replace("{ORIGIN}", self.origin).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain" if self.path.endswith(".txt") else "application/xml")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()


class RunAuditEndToEnd(unittest.TestCase):
    """run_audit.py against a real HTTP server on 127.0.0.1 serving tests/fixtures/site."""

    @classmethod
    def setUpClass(cls):
        handler = functools.partial(_FixtureHandler, directory=str(HERE / "fixtures" / "site"))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        _FixtureHandler.origin = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _run(self, out_dir: str) -> tuple[int, dict, str]:
        argv = ["--site", _FixtureHandler.origin + "/", "--out-dir", out_dir, "--delay", "0", "--timeout", "5",
                "--no-ai-access", "--thin-words", "20", "--probes", "3"]
        env = {k: v for k, v in os.environ.items()
               if k not in ("PAGESPEED_API_KEY", "CRUX_API_KEY", "GSC_SERVICE_ACCOUNT_FILE", "GSC_SITE")}
        env["INDEXNOW_KEY"] = "fixturekeyNEVERPRINTED42"
        out = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(out):
            code = run_audit.main(argv)
        folder = Path(out_dir) / f"127.0.0.1_{self.server.server_address[1]}"
        report = json.loads(sorted(folder.glob("audit_*.json"))[-1].read_text(encoding="utf-8"))
        return code, report, out.getvalue()

    def test_full_run_detects_the_planted_problems_and_leaks_no_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, report, log = self._run(tmp)
            codes = {f["code"]: f for f in report["findings"]}
            self.assertEqual(code, 0)  # no P0 planted
            self.assertIn("orphan-page", codes)
            self.assertTrue(codes["orphan-page"]["urls"][0].endswith("/lonely.html"))
            self.assertIn("broken-internal-link", codes)
            self.assertIn("generic-anchor", codes)
            self.assertIn("sitemap-noindex", codes)
            self.assertIn("cocoon-no-uplink", codes)
            self.assertIn("non-crawlable-link", codes)
            self.assertIn("indexnow-key-invalid", codes)  # fixture has no key file (and no HTTPS)
            self.assertTrue(report["summary"]["crawl_complete"])
            self.assertTrue(any(u.endswith("/private/admin.html") for u in report["summary"]["skipped_by_robots"]))
            self.assertTrue(all(p["status"] == 404 for p in report["probes_404"]))
            self.assertEqual(report["modules"]["pagespeed"]["status"], "skipped")
            folder = Path(tmp) / f"127.0.0.1_{self.server.server_address[1]}"
            md = next(folder.glob("audit_*.md")).read_text(encoding="utf-8")
            self.assertIn("## Plan de correction priorisé", md)
            everything = log + md + json.dumps(report)
            self.assertNotIn("fixturekeyNEVERPRINTED42", everything)

            # Second run: a diff against the first report is written automatically.
            import time
            time.sleep(1.1)  # report names are stamped to the second
            code2, report2, _ = self._run(tmp)
            self.assertEqual(code2, 0)
            self.assertTrue(report2["previous_report"])
            self.assertEqual(len(list(folder.glob("diff_*.md"))), 1)

    def test_markdown_renders_from_json_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            _code, report, _log = self._run(tmp)
            self.assertIn("Détail par page", report_markdown.render(report))


if __name__ == "__main__":
    unittest.main()
