"""Offline tests for validate_schema, htmlsignals and indexnow_submit.
Run: python -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import ai_bots  # noqa: E402
import check_ai_access  # noqa: E402
import generate_sitemap  # noqa: E402
import htmlsignals  # noqa: E402
import indexnow_submit  # noqa: E402
import robotstxt  # noqa: E402
import validate_schema  # noqa: E402


def _validate(raw: str) -> dict:
    return validate_schema.validate_blocks([raw], "t")[0]


class SchemaValidation(unittest.TestCase):
    def test_article_has_no_google_required_property(self):
        self.assertTrue(_validate('{"@context":"https://schema.org","@type":"NewsArticle","headline":"x"}')["valid"])

    def test_product_needs_offers_review_or_rating(self):
        r = _validate('{"@context":"https://schema.org","@type":"Product","name":"x"}')
        self.assertFalse(r["valid"])
        self.assertIn("offers ou review ou aggregateRating", r["error"])

    def test_graph_and_subtypes_are_checked(self):
        r = _validate('{"@context":"https://schema.org","@graph":[{"@type":"Restaurant","name":"x"}]}')
        self.assertFalse(r["valid"])
        self.assertIn("address", r["error"])
        self.assertEqual(r["types"], ["Restaurant"])

    def test_self_serving_rating_and_faq_are_warnings_not_errors(self):
        r = _validate('{"@context":"https://schema.org","@graph":['
                      '{"@type":"Organization","name":"x","aggregateRating":{"@type":"AggregateRating","ratingValue":5,"reviewCount":3}},'
                      '{"@type":"FAQPage","mainEntity":[]}]}')
        self.assertTrue(any("self-serving" in w for w in r["warnings"]))
        self.assertTrue(any("FAQPage" in w for w in r["warnings"]))

    def test_placeholders_and_broken_json_fail(self):
        self.assertFalse(_validate('{"@type":"Organization","name":"{{marque}}"}')["valid"])
        self.assertFalse(_validate("{ nope")["valid"])

    def test_list_item_position_required_only_in_breadcrumbs(self):
        crumbs = _validate('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","name":"a"}]}')
        self.assertFalse(crumbs["valid"])


class HtmlSignals(unittest.TestCase):
    def _parse(self, html: str, header: str | None = None) -> htmlsignals.PageSignals:
        s = htmlsignals.PageSignals(url="https://e.com/p", final_url="https://e.com/p", x_robots_tag=header)
        return htmlsignals.parse_html(s, html)

    def test_attribute_order_does_not_matter(self):
        s = self._parse('<html lang="fr"><meta content="D" name="description"><link href="/p" rel="canonical">')
        self.assertEqual(s.description, "D")
        self.assertEqual(s.canonical, "https://e.com/p")

    def test_tags_inside_scripts_and_svg_are_ignored(self):
        s = self._parse('<svg><title>icon</title></svg><title>Vrai</title><script>var x="<h1>"</script><h1>a</h1>')
        self.assertEqual(s.title, "Vrai")
        self.assertEqual(s.h1_count, 1)

    def test_noindex_from_header_and_nosnippet_from_meta(self):
        s = self._parse('<meta name="robots" content="max-snippet:0">', header="googlebot: noindex")
        self.assertTrue(s.noindex)
        self.assertTrue(s.nosnippet)

    def test_header_scoped_to_another_bot_is_ignored(self):
        s = self._parse("<title>x</title>", header="otherbot: noindex")
        self.assertFalse(s.noindex)

    def test_hreflang_is_resolved_to_absolute(self):
        s = self._parse('<link rel="alternate" hreflang="en" href="/en/p">')
        self.assertEqual(s.hreflang_links, [("en", "https://e.com/en/p")])


class IndexNowScope(unittest.TestCase):
    def test_key_outside_root_only_covers_its_directory(self):
        key_url = "https://example.com/indexnow/abc12345.txt"
        out = indexnow_submit.urls_outside_key_scope(["https://example.com/fr/robots", "https://example.com/indexnow/x"], key_url)
        self.assertEqual(out, ["https://example.com/fr/robots"])

    def test_root_key_covers_the_host(self):
        self.assertEqual(indexnow_submit.urls_outside_key_scope(["https://e.com/a/b"], "https://e.com/k1234567.txt"), [])

    def test_key_charset(self):
        self.assertTrue(indexnow_submit.KEY_RE.match("Abc-123456"))
        self.assertFalse(indexnow_submit.KEY_RE.match("short"))
        self.assertFalse(indexnow_submit.KEY_RE.match("has_underscore_1"))


class SitemapAndRobots(unittest.TestCase):
    def test_no_invented_lastmod_and_xml_is_escaped(self):
        xml = generate_sitemap.build_sitemap([{"url": "/a?x=1&y=2"}, {"url": "/b", "lastmod": "2026-09-20"}],
                                             "https://e.com")
        self.assertIn("<loc>https://e.com/a?x=1&amp;y=2</loc>", xml)
        self.assertEqual(xml.count("<lastmod>"), 1)
        self.assertNotIn("<priority>", xml)

    def test_search_only_blocks_training_and_tokens_but_not_citation(self):
        robots = robotstxt.parse(generate_sitemap.build_robots("https://e.com", "search-only"))
        for token in ("GPTBot", "ClaudeBot", "Google-Extended", "CCBot"):
            self.assertFalse(robotstxt.is_allowed(robots, token, "/"), token)
        for token in ("OAI-SearchBot", "Claude-SearchBot", "PerplexityBot", "Googlebot", "bingbot"):
            self.assertTrue(robotstxt.is_allowed(robots, token, "/"), token)


class CrawlerCatalog(unittest.TestCase):
    def test_tokens_are_unique_and_roles_known(self):
        tokens = [b.robots_token.lower() for b in ai_bots.AI_BOTS]
        self.assertEqual(len(tokens), len(set(tokens)))
        for bot in ai_bots.AI_BOTS:
            self.assertIn(bot.role, ("engine", "search", "user", "training", "token"))
            self.assertEqual(bot.ua is None, bot.role == "token", bot.robots_token)
            if bot.ua:
                self.assertIn(bot.robots_token.lower(), bot.ua.lower(), bot.robots_token)

    def test_robots_verdict_follows_http_status(self):
        robots = robotstxt.parse("User-agent: GPTBot\nDisallow: /\n")
        self.assertFalse(check_ai_access._robots_verdict(200, robots, "GPTBot", "/"))
        self.assertTrue(check_ai_access._robots_verdict(404, None, "GPTBot", "/"))
        self.assertFalse(check_ai_access._robots_verdict(503, None, "GPTBot", "/"))


if __name__ == "__main__":
    unittest.main()
