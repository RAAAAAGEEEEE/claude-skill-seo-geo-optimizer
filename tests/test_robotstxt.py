"""RFC 9309 behavior of scripts/robotstxt.py. Run: python -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import robotstxt  # noqa: E402


class GroupSemantics(unittest.TestCase):
    def test_rules_of_a_later_group_do_not_leak_into_star(self):
        # Regression: the previous parser applied GPTBot's rule to "*" too.
        robots = robotstxt.parse("User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /private\n")
        self.assertTrue(robotstxt.is_allowed(robots, "SomeBot", "/private"))
        self.assertFalse(robotstxt.is_allowed(robots, "GPTBot", "/private"))

    def test_other_records_do_not_end_a_group(self):
        # Regression: a Crawl-delay line used to re-route the next rule to "*".
        robots = robotstxt.parse("User-agent: GPTBot\nCrawl-delay: 5\nDisallow: /\n\nUser-agent: *\nAllow: /\n")
        self.assertFalse(robotstxt.is_allowed(robots, "GPTBot", "/"))
        self.assertTrue(robotstxt.is_allowed(robots, "ClaudeBot", "/"))

    def test_consecutive_user_agents_share_rules(self):
        robots = robotstxt.parse("User-agent: A\nUser-agent: B\nDisallow: /x\n")
        self.assertFalse(robotstxt.is_allowed(robots, "A", "/x"))
        self.assertFalse(robotstxt.is_allowed(robots, "B", "/x"))
        self.assertTrue(robotstxt.is_allowed(robots, "C", "/x"))  # no group, no "*": allowed

    def test_specific_group_replaces_star(self):
        robots = robotstxt.parse("User-agent: *\nDisallow: /\n\nUser-agent: ClaudeBot\nAllow: /\n")
        self.assertTrue(robotstxt.is_allowed(robots, "ClaudeBot", "/page"))
        self.assertFalse(robotstxt.is_allowed(robots, "Other", "/page"))

    def test_same_agent_groups_are_merged_and_case_insensitive(self):
        robots = robotstxt.parse("User-agent: gptbot\nDisallow: /a\n\nUser-agent: GPTBot/1.1\nDisallow: /b\n")
        self.assertFalse(robotstxt.is_allowed(robots, "GPTBot", "/a"))
        self.assertFalse(robotstxt.is_allowed(robots, "GPTBot", "/b"))


class RuleMatching(unittest.TestCase):
    def test_longest_match_wins(self):
        robots = robotstxt.parse("User-agent: *\nDisallow: /fr/\nAllow: /fr/robots\n")
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/fr/robots/g1"))
        self.assertFalse(robotstxt.is_allowed(robots, "x", "/fr/admin"))

    def test_allow_wins_a_tie(self):
        robots = robotstxt.parse("User-agent: *\nDisallow: /page\nAllow: /page\n")
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/page"))

    def test_wildcards(self):
        robots = robotstxt.parse("User-agent: *\nDisallow: /*.pdf$\nDisallow: /fr/comparateur?\n")
        self.assertFalse(robotstxt.is_allowed(robots, "x", "/docs/a.pdf"))
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/docs/a.pdf?v=2"))
        self.assertFalse(robotstxt.is_allowed(robots, "x", "/fr/comparateur?robots=a,b"))
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/fr/comparateur"))

    def test_empty_disallow_is_not_a_rule(self):
        robots = robotstxt.parse("User-agent: *\nDisallow:\n")
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/anything"))

    def test_robots_txt_is_always_allowed(self):
        robots = robotstxt.parse("User-agent: *\nDisallow: /\n")
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/robots.txt"))


class OtherRecords(unittest.TestCase):
    def test_sitemap_license_and_content_signal_are_exposed(self):
        robots = robotstxt.parse(
            "User-agent: *\nContent-Signal: search=yes, ai-train=no\nAllow: /\n"
            "Sitemap: https://e.com/sitemap.xml\nLicense: https://e.com/license.xml\n"
        )
        self.assertEqual(robots.records("sitemap"), ["https://e.com/sitemap.xml"])
        self.assertEqual(robots.records("license"), ["https://e.com/license.xml"])
        self.assertEqual(robots.records("content-signal"), ["search=yes, ai-train=no"])
        self.assertTrue(robotstxt.is_allowed(robots, "x", "/"))


class StatusHandling(unittest.TestCase):
    def test_status_codes(self):
        self.assertIsNone(robotstxt.verdict_for_status(200))
        self.assertEqual(robotstxt.verdict_for_status(404), "allow-all")
        self.assertEqual(robotstxt.verdict_for_status(503), "disallow-all")
        self.assertEqual(robotstxt.verdict_for_status(429), "disallow-all")  # Google: 429 = 5xx
        self.assertEqual(robotstxt.verdict_for_status(None), "disallow-all")


if __name__ == "__main__":
    unittest.main()
