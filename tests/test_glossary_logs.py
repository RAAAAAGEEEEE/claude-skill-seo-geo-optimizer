"""Offline tests for 2.2.0: glossary_check.py (build, audit, linking
opportunities, term suggestions) and crawler_logs.py (log parsing, crawler
identification, IP verification against vendor lists, findings, privacy).

Run: python -m unittest discover -s tests
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import crawler_logs  # noqa: E402
import glossary_check as g  # noqa: E402

GLOSSARY = HERE / "fixtures" / "glossary"
LOGS = HERE / "fixtures" / "logs"


def _page(name: str, url: str) -> g.Page:
    return g.parse_page(url, (GLOSSARY / name).read_text(encoding="utf-8"))


class GlossaryBuild(unittest.TestCase):
    def setUp(self):
        self.terms = g.load_terms(GLOSSARY / "terms.csv")

    def test_issues_missing_duplicate_short(self):
        codes = {(i["code"], i["blocking"]) for i in g.check_terms(self.terms)}
        self.assertIn(("term-missing-definition", True), codes)
        self.assertIn(("term-duplicate", True), codes)
        self.assertIn(("definition-short", False), codes)  # heuristic, CLAIMED, never blocking

    def test_jsonld_only_from_complete_rows_and_matches_html(self):
        data = g.build_jsonld(self.terms, "Lexique", "https://e.test/fr/lexique", "fr")
        names = [t["name"] for t in data["hasDefinedTerm"]]
        self.assertNotIn("Préhenseur", names)  # no definition: never invented
        self.assertEqual(data["@type"], "DefinedTermSet")
        ddl = next(t for t in data["hasDefinedTerm"] if t["name"] == "Degré de liberté")
        self.assertEqual(ddl["url"], "https://e.test/fr/lexique#ddl")
        self.assertEqual(ddl["termCode"], "DoF")
        self.assertEqual(ddl["inDefinedTermSet"], {"@id": "https://e.test/fr/lexique#lexique"})
        cobot = next(t for t in data["hasDefinedTerm"] if t["name"] == "Cobot")
        self.assertEqual(cobot["sameAs"], ["https://www.wikidata.org/wiki/Q1142726"])
        markup = g.build_html(self.terms, "https://e.test/fr/lexique")
        for t in data["hasDefinedTerm"]:
            self.assertIn(f"<dfn>{t['name']}</dfn>", markup)  # markup describes visible text
        self.assertIn('<dt id="ddl">', markup)
        self.assertEqual(markup.count('id="cobot"'), 1)  # the duplicate row is reported, not published
        self.assertEqual(names.count("Cobot") + names.count("cobot"), 1)

    def test_build_cli_writes_both_files_and_fails_on_blocking(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            rc = g.main(["build", "--terms", str(GLOSSARY / "terms.csv"), "--set-name", "Lexique",
                         "--set-url", "https://e.test/fr/lexique", "--out-dir", tmp])
            self.assertEqual(rc, 1)
            self.assertTrue((Path(tmp) / "glossary.html").exists())
            raw = (Path(tmp) / "glossary.jsonld").read_text(encoding="utf-8")
            json.loads(raw.split(">", 1)[1].rsplit("</script>", 1)[0])  # valid JSON inside the script tag


class GlossaryAudit(unittest.TestCase):
    def setUp(self):
        self.page = _page("lexique.html", "https://e.test/fr/lexique")
        self.result = g.audit_glossary_page(self.page)

    def test_terms_found_from_jsonld_and_markup(self):
        names = {t["term"] for t in self.result["terms"]}
        self.assertTrue({"Cobot", "LiDAR", "Préhenseur", "Exosquelette"} <= names)
        self.assertEqual(self.result["jsonld_terms"], 4)

    def test_invisible_markup_and_broken_anchor_are_blocking(self):
        by_code = {}
        for i in self.result["issues"]:
            by_code.setdefault(i["code"], []).append(i)
        self.assertIn("Exosquelette", by_code["jsonld-term-not-visible"][0]["detail"])
        self.assertTrue(by_code["jsonld-term-not-visible"][0]["blocking"])
        anchors = " ".join(i["detail"] for i in by_code["term-anchor-missing"])
        self.assertIn("#prehenseur", anchors)  # <dt> without id
        self.assertNotIn("#cobot", anchors)
        self.assertFalse(by_code["definition-short"][0]["blocking"])

    def test_linking_opportunities_first_mention_and_plural(self):
        pages = [self.page, _page("article-a.html", "https://e.test/fr/a"), _page("article-b.html", "https://e.test/fr/b")]
        lk = g.mention_opportunities(self.result["terms"], pages, "https://e.test/fr/lexique")
        opp = {o["term"]: o["pages"] for o in lk["opportunities"]}
        # article-a mentions "cobots" and links to the hub only from its menu: not a link to the definition
        self.assertIn("https://e.test/fr/a", opp["Cobot"])
        self.assertNotIn("https://e.test/fr/b", opp["Cobot"])  # article-b links #cobot
        # article-b links #cobot but mentions préhenseur (accent-insensitive) and LIDAR without a link to them
        self.assertIn("https://e.test/fr/b", opp["Préhenseur"])
        self.assertIn("https://e.test/fr/b", opp["LiDAR"])
        self.assertIn("Exosquelette", lk["terms_never_mentioned"])
        self.assertEqual(lk["pages_scanned"], 3)

    def test_hub_with_one_page_per_term(self):
        hub = g.parse_page("https://e.test/fr/glossaire",
                           '<main><h2 id="a">A</h2><a href="/fr/definition/cobot">Cobot</a>'
                           '<a href="/fr/definition/cobot">Cobot</a><a href="/fr/contact">Contact</a></main>')
        terms = g.extract_terms(hub, "/fr/definition/")
        self.assertEqual([(t["term"], t["url"]) for t in terms], [("Cobot", "https://e.test/fr/definition/cobot")])
        page = g.parse_page("https://e.test/fr/x", "<main><p>Un cobot, voir <a href='/fr/glossaire'>lexique</a>.</p></main>")
        lk = g.mention_opportunities(terms, [page], "https://e.test/fr/glossaire")
        self.assertEqual(lk["opportunities"][0]["pages"], ["https://e.test/fr/x"])  # hub link is not the definition

    def test_suggest_acronyms_and_abbr_minus_known_terms(self):
        pages = [_page("article-a.html", "https://e.test/fr/a"), _page("article-b.html", "https://e.test/fr/b")]
        cands = {c["term"]: c for c in g.suggest_terms(pages, known={"LiDAR"}, min_pages=2)}
        self.assertIn("ROS", cands)
        self.assertEqual(cands["ROS"]["pages"], 2)
        self.assertNotIn("LiDAR", cands)
        self.assertNotIn("LIDAR", cands)  # known terms compared without case


class CrawlerLogs(unittest.TestCase):
    def setUp(self):
        tokens = {c.token.lower() for c in crawler_logs.catalogue()}
        self.ranges, self.status = crawler_logs.load_ranges(tokens, LOGS / "ranges")
        lines = (LOGS / "access.log").read_text(encoding="utf-8").splitlines()
        self.result = crawler_logs.analyze(lines, self.ranges)

    def test_parsing_combined_and_json_lines(self):
        self.assertEqual(self.result["parsed"], 10)
        self.assertEqual(self.result["unparsed"], 1)
        self.assertEqual(self.result["bot_hits"], 9)  # the Chrome request is not a crawler

    def test_identification_prefers_specific_tokens(self):
        self.assertEqual(crawler_logs.identify("Mozilla/5.0 (compatible; Google-InspectionTool/1.0;)").token,
                         "Google-InspectionTool")
        self.assertEqual(crawler_logs.identify("x; ChatGPT-User/1.0; +https://openai.com/bot").token, "ChatGPT-User")
        self.assertIsNone(crawler_logs.identify("Mozilla/5.0 (Windows NT 10.0) Chrome/140.0"))

    def test_verification_against_vendor_lists(self):
        bots = self.result["bots"]
        self.assertEqual(bots["Googlebot"].verified, 4)
        self.assertEqual(bots["Googlebot"].spoofed, 1)  # 203.0.113.7 claims Googlebot
        self.assertEqual(bots["GPTBot"].spoofed, 1)
        self.assertEqual(bots["OAI-SearchBot"].verified, 1)
        self.assertEqual(bots["meta-externalagent"].unverifiable, 1)  # Meta publishes no list

    def test_findings_and_blocking(self):
        fnd = crawler_logs.findings(self.result, ["/fr", "/fr/robots/atlas", "/fr/guides"])
        codes = {(f["code"], f["blocking"]) for f in fnd}
        self.assertIn(("crawler-5xx-429", True), codes)  # 503 to Googlebot
        self.assertIn(("robots-txt-not-200", True), codes)  # robots.txt 500 to bingbot
        self.assertIn(("spoofed-crawler", False), codes)
        cov = next(f for f in fnd if f["code"] == "sitemap-url-not-crawled" and f["detail"].startswith("Googlebot"))
        self.assertIn("/fr/guides", cov["detail"])  # only a 503: not crawled successfully
        top404 = next(f for f in fnd if f["code"] == "crawler-404")
        self.assertIn("/fr/robots/ancien (2)", top404["detail"])

    def test_no_ip_address_in_outputs(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as out:
            rc = crawler_logs.main([str(LOGS / "access.log"), "--ranges-dir", str(LOGS / "ranges"),
                                    "--json", str(Path(tmp) / "r.json"), "--md", str(Path(tmp) / "r.md")])
            text = out.getvalue() + (Path(tmp) / "r.json").read_text(encoding="utf-8") \
                + (Path(tmp) / "r.md").read_text(encoding="utf-8")
        self.assertEqual(rc, 1)
        for ip in ("66.249.66.1", "203.0.113.7", "20.171.207.5", "157.55.39.10", "198.51.100.20"):
            self.assertNotIn(ip, text)
        self.assertIn("203.0.113.0/24", text)  # spoofed source aggregated

    def test_no_verify_makes_no_claim(self):
        result = crawler_logs.analyze((LOGS / "access.log").read_text(encoding="utf-8").splitlines(), None)
        self.assertEqual(result["bots"]["Googlebot"].verified, 0)
        self.assertEqual(result["bots"]["Googlebot"].unverifiable, 5)


if __name__ == "__main__":
    unittest.main()
