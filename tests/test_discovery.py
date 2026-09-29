"""Offline tests for search_console.py and url_discovery.py (2.4.0).

Every HTTP call goes through an injected fake: no request leaves the machine,
no Google library is needed.

Run: python -m unittest discover -s tests
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import search_console as sc  # noqa: E402
import url_discovery as ud  # noqa: E402

NOW = datetime(2026, 9, 30, 8, 0, tzinfo=timezone.utc)
TOKEN = "fake-oauth-token-never-printed"


def _idx(verdict="NEUTRAL", coverage="", fetch="SUCCESSFUL", indexing="INDEXING_ALLOWED",
         robots="ALLOWED", google=None, user=None):
    d = {"verdict": verdict, "coverageState": coverage, "pageFetchState": fetch,
         "indexingState": indexing, "robotsTxtState": robots}
    if google:
        d["googleCanonical"] = google
    if user:
        d["userCanonical"] = user
    return {"inspectionResult": {"indexStatusResult": d, "inspectionResultLink": "https://search.google.com/x"}}


class FakeClient:
    """Stands in for sc.SearchConsole."""

    def __init__(self, results=None, fail=None, sitemaps=None):
        self.results = results or {}
        self.fail = fail or {}
        self.known_sitemaps = sitemaps or []
        self.inspected, self.submitted = [], []

    def inspect(self, site, url, language="en-US"):
        self.inspected.append(url)
        if url in self.fail:
            raise self.fail[url]
        return self.results.get(url, _idx("PASS", "Submitted and indexed"))

    def sitemaps(self, site):
        return self.known_sitemaps

    def submit_sitemap(self, site, feed):
        self.submitted.append(feed)


class Classify(unittest.TestCase):
    def test_categories_from_enum_fields(self):
        cases = {
            "indexed": _idx("PASS", "Submitted and indexed"),
            "unknown_to_google": _idx(coverage="URL is unknown to Google", fetch="PAGE_FETCH_STATE_UNSPECIFIED"),
            "discovered_not_crawled": _idx(coverage="Discovered - currently not indexed",
                                           fetch="PAGE_FETCH_STATE_UNSPECIFIED"),
            "crawled_not_indexed": _idx(coverage="Crawled - currently not indexed"),
            "blocked_robots_txt": _idx(robots="DISALLOWED"),
            "noindex": _idx(indexing="BLOCKED_BY_META_TAG"),
            "fetch_error": _idx("FAIL", fetch="NOT_FOUND"),
            "canonical_elsewhere": _idx(google="https://e.com/a", user="https://e.com/b"),
        }
        for expected, response in cases.items():
            with self.subTest(expected=expected):
                s = sc.summarize("https://e.com/p", response)
                self.assertEqual(s["category"], expected)
                self.assertTrue(s["next_step"])

    def test_order_priority_then_newest(self):
        entries = [("https://e.com/old", "2026-01-01"), ("https://e.com/new", "2026-09-01"),
                   ("https://e.com/none", None), ("https://e.com/home", "2025-01-01")]
        self.assertEqual(sc.order_urls(entries, ["https://e.com/home", "https://e.com/absent"]),
                         ["https://e.com/home", "https://e.com/new", "https://e.com/old", "https://e.com/none"])


class Inspection(unittest.TestCase):
    def run_insp(self, client, urls, state=None, **kw):
        return sc.run_inspection(client, "sc-domain:e.com", urls, {} if state is None else state,
                                 now=NOW, sleep=lambda s: None, **kw)

    def test_not_indexed_listed_and_requestable_limited(self):
        urls = [f"https://e.com/{i}" for i in range(6)]
        results = {u: _idx(coverage="Discovered - currently not indexed", fetch="PAGE_FETCH_STATE_UNSPECIFIED")
                   for u in urls[:4]}
        results[urls[4]] = _idx(indexing="BLOCKED_BY_META_TAG")
        r = self.run_insp(FakeClient(results), urls, max_request=2)
        self.assertEqual(r["inspected"], 6)
        self.assertEqual(r["indexed"], 1)
        self.assertEqual(len(r["not_indexed"]), 5)
        self.assertEqual(r["to_request"], urls[:2])  # noindex never proposed, cap respected
        self.assertEqual(r["by_category"], {"discovered_not_crawled": 4, "noindex": 1})

    def test_recently_indexed_skipped_and_recently_requested_not_proposed(self):
        state = {"https://e.com/a": {"category": "indexed", "inspected_at": (NOW - timedelta(days=2)).isoformat()},
                 "https://e.com/b": {"requested_at": (NOW - timedelta(days=1)).isoformat()}}
        client = FakeClient({"https://e.com/b": _idx(coverage="Crawled - currently not indexed")})
        r = self.run_insp(client, ["https://e.com/a", "https://e.com/b"], state)
        self.assertEqual(client.inspected, ["https://e.com/b"])
        self.assertEqual(r["skipped_recently_indexed"], 1)
        self.assertEqual(r["to_request"], [])
        self.assertEqual(state["https://e.com/b"]["category"], "crawled_not_indexed")

    def test_quota_stops_and_keeps_results(self):
        client = FakeClient(fail={"https://e.com/2": sc.ApiError(429, "Quota exceeded")})
        r = self.run_insp(client, ["https://e.com/1", "https://e.com/2", "https://e.com/3"])
        self.assertTrue(r["quota_stopped"])
        self.assertEqual(r["inspected"], 1)
        self.assertNotIn("https://e.com/3", client.inspected)

    def test_three_consecutive_errors_stop(self):
        fail = {f"https://e.com/{i}": sc.ApiError(500, "boom") for i in range(5)}
        client = FakeClient(fail=fail)
        r = self.run_insp(client, list(fail))
        self.assertEqual(len(client.inspected), 3)
        self.assertEqual(len(r["errors"]), 3)

    def test_daily_quota_is_a_hard_cap(self):
        urls = [f"https://e.com/{i}" for i in range(2100)]
        r = self.run_insp(FakeClient(), urls, max_inspect=5000)
        self.assertEqual(r["inspected"], sc.INSPECT_DAILY_QUOTA)

    def test_mark_requested(self):
        state = {}
        self.assertEqual(sc.mark_requested(state, ["https://e.com/a"], NOW), 1)
        self.assertEqual(state["https://e.com/a"]["requested_at"], NOW.isoformat())


class RestClient(unittest.TestCase):
    def make(self, responses):
        calls = []

        def transport(method, url, headers, body):
            calls.append((method, url, headers, body))
            return responses.pop(0)
        return sc.SearchConsole(TOKEN, transport=transport, sleep=lambda s: None), calls

    def test_submit_sitemap_is_a_put_with_encoded_path(self):
        client, calls = self.make([(200, b"")])
        client.submit_sitemap("sc-domain:e.com", "https://e.com/sitemap.xml")
        method, url, headers, body = calls[0]
        self.assertEqual(method, "PUT")
        self.assertEqual(url, "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Ae.com/sitemaps/"
                              "https%3A%2F%2Fe.com%2Fsitemap.xml")
        self.assertIsNone(body)
        self.assertEqual(headers["Authorization"], f"Bearer {TOKEN}")

    def test_inspect_body_and_retry_on_5xx(self):
        client, calls = self.make([(503, b"{}"), (200, json.dumps(_idx("PASS")).encode())])
        client.inspect("https://e.com/", "https://e.com/p")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][1], sc.INSPECT_ENDPOINT)
        self.assertEqual(json.loads(calls[1][3]), {"inspectionUrl": "https://e.com/p", "siteUrl": "https://e.com/",
                                                   "languageCode": "en-US"})

    def test_error_message_never_contains_the_token(self):
        client, _ = self.make([(403, json.dumps({"error": {"message": f"denied for {TOKEN}"}}).encode())])
        with self.assertRaises(sc.ApiError) as ctx:
            client.sitemaps("sc-domain:e.com")
        self.assertEqual(ctx.exception.status, 403)
        self.assertNotIn(TOKEN, str(ctx.exception))

    def test_quota_flag(self):
        self.assertTrue(sc.ApiError(429, "x").quota)
        self.assertTrue(sc.ApiError(403, "Quota exceeded for quota metric").quota)
        self.assertFalse(sc.ApiError(403, "User does not have sufficient permission").quota)


class Cli(unittest.TestCase):
    def test_no_access_exits_2(self):
        with mock.patch.dict(os.environ, {"GSC_ACCESS_TOKEN": "", "GSC_SERVICE_ACCOUNT_FILE": ""}), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(sc.main(["sites"]), 2)
        self.assertIn("gsc-access.md", err.getvalue())

    def test_submit_dry_run_calls_nothing(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(sc.main(["submit-sitemap", "--site", "sc-domain:e.com",
                                      "--sitemap", "https://e.com/s.xml", "--dry-run"]), 0)
        self.assertIn("--dry-run", out.getvalue())

    def test_inspect_with_url_file_and_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            urls = Path(tmp, "urls.txt")
            urls.write_text("https://e.com/a\n# comment\nhttps://e.com/b\n", encoding="utf-8")
            state, out = Path(tmp, "state.json"), Path(tmp, "out.json")
            client = FakeClient({"https://e.com/b": _idx(coverage="URL is unknown to Google",
                                                          fetch="PAGE_FETCH_STATE_UNSPECIFIED")})
            with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(sc.time, "sleep"):
                code = sc.main(["inspect", "--site", "https://e.com/", "--urls", str(urls),
                                "--state", str(state), "--out", str(out)], client=client)
            self.assertEqual(code, 0)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["to_request"], ["https://e.com/b"])
            self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["https://e.com/a"]["category"], "indexed")
            with contextlib.redirect_stdout(io.StringIO()):
                sc.main(["mark-requested", "--state", str(state), "https://e.com/b"])
            self.assertIn("requested_at", json.loads(state.read_text(encoding="utf-8"))["https://e.com/b"])


ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<link rel="hub" href="https://pubsubhubbub.appspot.com/"/><link rel="self" href="https://e.com/feed.xml"/>
<title>t</title></feed>"""
RSS_NO_HUB = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title></channel></rss>"""


class FeedParsing(unittest.TestCase):
    def test_atom_hub_and_self(self):
        info = ud.feed_hubs(ATOM, {})
        self.assertEqual((info["format"], info["hubs"], info["self"]),
                         ("atom", ["https://pubsubhubbub.appspot.com/"], "https://e.com/feed.xml"))

    def test_rss_atom_link_and_http_header(self):
        rss = (b'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
               b'<atom:link rel="hub" href="https://hub.example/"/></channel></rss>')
        self.assertEqual(ud.feed_hubs(rss, {})["hubs"], ["https://hub.example/"])
        info = ud.feed_hubs(RSS_NO_HUB, {"Link": '<https://hub.example/>; rel="hub", <https://e.com/f>; rel="self"'})
        self.assertEqual((info["format"], info["hubs"], info["self"]), ("rss", ["https://hub.example/"], "https://e.com/f"))

    def test_home_page_feeds_and_links(self):
        html = ('<link rel="alternate" type="application/rss+xml" href="/feed.xml">'
                '<a href="/fr/new/">N</a><a href="mailto:x@e.com">m</a><a href="#top">t</a>')
        feeds, links = ud.parse_page(html, "https://e.com/")
        self.assertEqual(feeds, ["https://e.com/feed.xml"])
        self.assertEqual(links, {"https://e.com/fr/new"})

    def test_diff(self):
        self.assertTrue(ud.diff_entries(None, {"a": None})["baseline"])
        d = ud.diff_entries({"a": "1", "b": "1", "c": "1"}, {"a": "1", "b": "2", "d": None})
        self.assertEqual((d["new"], d["modified"], d["removed"]), (["d"], ["b"], ["c"]))


def _sitemap(entries):
    rows = "".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod></url>" for u, m in entries)
    return f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>'.encode()


class FakeSite:
    def __init__(self, entries, robots="User-agent: *\nAllow: /\nSitemap: https://e.com/sitemap.xml\n",
                 home='<link rel="alternate" type="application/atom+xml" href="/feed.xml"><a href="/a">A</a>'):
        self.pages = {"https://e.com/": home.encode(), "https://e.com/robots.txt": robots.encode(),
                      "https://e.com/sitemap.xml": _sitemap(entries), "https://e.com/feed.xml": ATOM}
        self.posts = []

    def get(self, url, timeout=20.0):
        body = self.pages.get(url)
        return (200, body, {}) if body is not None else (404, None, {})

    def post(self, url, fields, timeout=20.0):
        self.posts.append((url, fields))
        return 204, ""


class DiscoveryEndToEnd(unittest.TestCase):
    def run_disc(self, site, tmp, extra=(), client=None):
        argv = ["--site", "https://e.com", "--gsc-site", "sc-domain:e.com", "--out-dir", tmp, *extra]
        with contextlib.redirect_stdout(io.StringIO()) as out, \
                mock.patch.dict(os.environ, {"INDEXNOW_KEY": ""}):
            code = ud.main(argv, get=site.get, post=site.post, gsc_client=client, now=NOW, sleep=lambda s: None)
        folder = Path(tmp, "e.com")
        report = json.loads(sorted(folder.glob("discovery_2*.json"))[-1].read_text(encoding="utf-8"))
        state = json.loads((folder / "discovery_state.json").read_text(encoding="utf-8"))
        return code, report, state, out.getvalue()

    def test_baseline_then_new_page_is_announced(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FakeClient(sitemaps=[{"path": "https://e.com/sitemap.xml", "errors": "0"}])
            site = FakeSite([("https://e.com/a", "2026-09-01"), ("https://e.com/b", "2026-09-02")])
            code, report, state, _ = self.run_disc(site, tmp, ["--submit"], client)
            self.assertEqual(code, 0)
            self.assertTrue(report["changes"]["baseline"])
            self.assertEqual(client.submitted, [])  # nothing new on a baseline
            self.assertEqual(site.posts, [])

            site.pages["https://e.com/sitemap.xml"] = _sitemap([("https://e.com/a", "2026-09-01"),
                                                                ("https://e.com/b", "2026-09-29"),
                                                                ("https://e.com/c", "2026-09-30")])
            code, report, state, _ = self.run_disc(site, tmp, ["--submit"], client)
            self.assertEqual(report["changes"]["new"], ["https://e.com/c"])
            self.assertEqual(report["changes"]["modified"], ["https://e.com/b"])
            self.assertEqual(client.submitted, ["https://e.com/sitemap.xml"])
            self.assertEqual(site.posts, [("https://pubsubhubbub.appspot.com/",
                                           [("hub.mode", "publish"), ("hub.url", "https://e.com/feed.xml")])])
            self.assertEqual(state["pending"], [])
            self.assertEqual(report["steps"]["indexnow"]["status"], "skipped")
            self.assertEqual(report["steps"]["linking"]["not_linked"], ["https://e.com/c"])
            self.assertEqual(code, 0)  # an orphan is a P1 finding, not a failed action

    def test_without_submit_nothing_leaves_and_pending_is_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FakeClient(sitemaps=[{"path": "https://e.com/sitemap.xml"}])
            site = FakeSite([("https://e.com/a", "2026-09-01")])
            self.run_disc(site, tmp, client=client)
            site.pages["https://e.com/sitemap.xml"] = _sitemap([("https://e.com/a", "2026-09-01"),
                                                                ("https://e.com/n", "2026-09-30")])
            _, report, state, _ = self.run_disc(site, tmp, client=client)
            self.assertEqual((client.submitted, site.posts), ([], []))
            self.assertEqual(state["pending"], ["https://e.com/n"])
            self.assertEqual(report["steps"]["search_console"]["would_submit"], ["https://e.com/sitemap.xml"])
            self.assertIn("--submit absent", report["steps"]["websub"]["detail"])
            _, report, state, _ = self.run_disc(site, tmp, ["--submit"], client)
            self.assertEqual(client.submitted, ["https://e.com/sitemap.xml"])  # pending survived the dry run
            self.assertEqual(state["pending"], [])

    def test_findings_robots_without_sitemap_and_unsubmitted_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = FakeSite([("https://e.com/a", "2026-09-01")], robots="User-agent: *\nAllow: /\n")
            _, report, _, _ = self.run_disc(site, tmp, client=FakeClient(sitemaps=[]))
            messages = " ".join(f["message"] for f in report["findings"])
            self.assertIn("Sitemap:", messages)
            self.assertIn("non soumis dans Search Console", messages)

    def test_inspection_runs_new_urls_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FakeClient(sitemaps=[{"path": "https://e.com/sitemap.xml"}],
                                results={"https://e.com/n": _idx(coverage="URL is unknown to Google",
                                                                  fetch="PAGE_FETCH_STATE_UNSPECIFIED")})
            site = FakeSite([("https://e.com/a", "2026-09-01")])
            self.run_disc(site, tmp, client=client)
            site.pages["https://e.com/sitemap.xml"] = _sitemap([("https://e.com/a", "2026-09-01"),
                                                                ("https://e.com/n", "2026-08-01")])
            _, report, state, out = self.run_disc(site, tmp, ["--inspect", "1"], client)
            self.assertEqual(client.inspected, ["https://e.com/n"])
            self.assertEqual(report["inspection"]["to_request"], ["https://e.com/n"])
            self.assertIn("https://e.com/n", state["inspection"])
            md = sorted(Path(tmp, "e.com").glob("discovery_2*.md"))[-1].read_text(encoding="utf-8")
            self.assertIn("unknown_to_google", md)

    def test_unreachable_site_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = FakeSite([])
            site.pages.pop("https://e.com/")
            code, report, _, _ = self.run_disc(site, tmp)
            self.assertEqual(code, 2)
            self.assertTrue(report["unreachable"])

    def test_indexnow_key_never_written(self):
        key = "0123456789abcdef0123456789abcdef"
        with tempfile.TemporaryDirectory() as tmp:
            site = FakeSite([("https://e.com/a", "2026-09-01")])
            argv = ["--site", "https://e.com", "--out-dir", tmp]
            with contextlib.redirect_stdout(io.StringIO()) as out, \
                    mock.patch.dict(os.environ, {"INDEXNOW_KEY": key, "GSC_SITE": ""}):
                ud.main(argv, get=site.get, post=site.post, now=NOW)
            written = "".join(p.read_text(encoding="utf-8") for p in Path(tmp).rglob("*") if p.is_file())
            self.assertNotIn(key, written + out.getvalue())


if __name__ == "__main__":
    unittest.main()
