"""Tests hors ligne de 2.8.0 : trust_check.py (HTTPS, en-tetes, security.txt, identite, lastmod)."""
import json
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import trust_check as t  # noqa: E402


def req(table):
    def r(url, timeout=15.0, follow=True):
        return table.get(url, (404, {}, ""))
    return r


class Headers(unittest.TestCase):
    def test_all_missing(self):
        r = req({"https://x.fr/": (200, {}, ""), "http://x.fr/": (200, {}, "")})
        codes = {c for c, _, _ in t.check_headers("https://x.fr", r)}
        self.assertEqual(codes, {"http-no-redirect", "hsts-missing", "security-headers-missing"})

    def test_clean(self):
        h = {"strict-transport-security": "max-age=31536000", "x-content-type-options": "nosniff",
             "referrer-policy": "strict-origin-when-cross-origin"}
        r = req({"https://x.fr/": (200, h, ""), "http://x.fr/": (301, {"location": "https://x.fr/"}, "")})
        self.assertEqual(t.check_headers("https://x.fr", r), [])

    def test_unreachable_no_verdict(self):
        self.assertEqual(t.check_headers("https://x.fr", req({"https://x.fr/": (503, {}, "")})), [])


class SecurityTxt(unittest.TestCase):
    U = "https://x.fr/.well-known/security.txt"

    def test_missing_expired_ok(self):
        today = date(2026, 11, 5)
        self.assertEqual(t.check_security_txt("https://x.fr", req({}), today)[0][0], "security-txt-missing")
        old = req({self.U: (200, {}, "Contact: mailto:a@x.fr\nExpires: 2026-01-01T00:00:00Z")})
        self.assertEqual(t.check_security_txt("https://x.fr", old, today)[0][0], "security-txt-expired")
        ok = req({self.U: (200, {}, "Contact: mailto:a@x.fr\nExpires: 2027-10-31T00:00:00Z")})
        self.assertEqual(t.check_security_txt("https://x.fr", ok, today), [])


class Identity(unittest.TestCase):
    def test_org(self):
        bad = [json.dumps({"@type": "Organization", "name": "X"})]
        self.assertEqual({c for c, _, _ in t.check_identity(bad)}, {"org-sameas-missing", "org-contact-missing"})
        good = [json.dumps({"@graph": [{"@type": "Organization", "sameAs": ["https://x.com/a"], "email": "a@x.fr"}]})]
        self.assertEqual(t.check_identity(good), [])
        self.assertEqual(t.check_identity([]), [])


class Lastmod(unittest.TestCase):
    def test_mismatch_and_unmeasurable(self):
        pairs = [("a", "2026-11-04", date(2026, 8, 1)), ("b", "2026-11-04", date(2026, 11, 4)), ("c", "2026-11-04", None)]
        self.assertEqual([u for u, _ in t.check_lastmod_vs_page(pairs)], ["a"])

    def test_page_date(self):
        b = [json.dumps({"@type": "Article", "dateModified": "2026-10-02"})]
        self.assertEqual(t.page_modified_date(b, []), date(2026, 10, 2))
        self.assertEqual(t.page_modified_date([], [{"property": "article:modified_time", "content": "2026-09-01T10:00:00Z"}]), date(2026, 9, 1))


if __name__ == "__main__":
    unittest.main()
