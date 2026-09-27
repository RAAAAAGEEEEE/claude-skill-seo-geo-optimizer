#!/usr/bin/env python3
"""robots.txt matcher following RFC 9309 (Robots Exclusion Protocol, 2022).

Why a dedicated module: the standard library's urllib.robotparser applies the
first matching rule, not the longest one, and ignores the `*` / `$` wildcards
that Google, Bing and the AI crawlers honor. A wrong verdict here produces a
wrong audit, so the semantics are spelled out and tested
(tests/test_robotstxt.py):

- A group is one or more consecutive `user-agent` lines followed by rules. It
  ends at the next `user-agent` line that follows a rule. Other records
  (`sitemap`, `crawl-delay`, `license`, `content-signal`...) do not end a group.
- The crawler obeys every group whose user-agent matches its product token
  (case-insensitive), merged. If none matches, it obeys the `*` group. If there
  is no `*` group either, everything is allowed.
- Among the rules of that merged group, the longest matching pattern wins.
  On a tie between `allow` and `disallow`, `allow` wins.
- `*` matches any sequence of characters, a trailing `$` anchors the end.
- `/robots.txt` itself is always allowed.
- HTTP status of robots.txt: 4xx means "no restriction", 5xx or unreachable
  means "assume everything is disallowed" (RFC 9309 section 2.3.1). Google
  treats 429 like a 5xx (robots.txt spec, updated 2026-08-31); so does this
  module, since the strictest reading is the safe one for an audit.

Usage as a CLI (debugging):
    python robotstxt.py https://example.com/robots.txt GPTBot /some/path
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field

MAX_BYTES = 500 * 1024  # RFC 9309: parse at least the first 500 KiB


@dataclass
class Group:
    agents: list[str] = field(default_factory=list)
    rules: list[tuple[str, str]] = field(default_factory=list)  # (allow|disallow, pattern)


@dataclass
class RobotsTxt:
    groups: list[Group]
    other_records: list[tuple[str, str]]  # (field lowercased, raw value) e.g. sitemap, license

    def records(self, name: str) -> list[str]:
        """Values of a non-group record, e.g. records("sitemap")."""
        return [value for key, value in self.other_records if key == name.lower()]


def _product_token(value: str) -> str:
    """'Googlebot/2.1' -> 'googlebot'. '*' stays '*'."""
    value = value.strip()
    if value == "*":
        return "*"
    match = re.match(r"[A-Za-z_\-]+", value)
    return match.group(0).lower() if match else value.lower()


def parse(text: str) -> RobotsTxt:
    text = text.encode("utf-8")[:MAX_BYTES].decode("utf-8", errors="ignore")
    groups: list[Group] = []
    other: list[tuple[str, str]] = []
    current: Group | None = None
    last_was_agent = False

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            if current is None or not last_was_agent:
                current = Group()
                groups.append(current)
            current.agents.append(_product_token(value))
            last_was_agent = True
        elif key in ("allow", "disallow"):
            last_was_agent = False
            if current is None:
                continue  # rule before any user-agent line: ignored by the RFC
            if value == "":
                continue  # "Disallow:" with no path is not a rule
            current.rules.append((key, value))
        else:
            # Non-group record. Deliberately does not end the current group.
            other.append((key, value))
    return RobotsTxt(groups=groups, other_records=other)


def _pattern_to_regex(pattern: str) -> re.Pattern[str]:
    anchored = pattern.endswith("$")
    if anchored:
        pattern = pattern[:-1]
    regex = ".*".join(re.escape(part) for part in pattern.split("*"))
    return re.compile(regex + ("$" if anchored else ""))


def rules_for(robots: RobotsTxt, user_agent_token: str) -> list[tuple[str, str]] | None:
    """Merged rules of the groups that apply to this token. None = no group applies."""
    token = _product_token(user_agent_token)
    matching = [g for g in robots.groups if token in g.agents]
    if not matching:
        matching = [g for g in robots.groups if "*" in g.agents]
    if not matching:
        return None
    merged: list[tuple[str, str]] = []
    for group in matching:
        merged.extend(group.rules)
    return merged


def is_allowed(robots: RobotsTxt, user_agent_token: str, path: str = "/") -> bool:
    if not path.startswith("/"):
        path = "/" + path
    if path == "/robots.txt":
        return True
    rules = rules_for(robots, user_agent_token)
    if not rules:
        return True

    best_len = -1
    best_allow = True
    for directive, pattern in rules:
        if not _pattern_to_regex(pattern).match(path):
            continue
        length = len(pattern)
        allow = directive == "allow"
        if length > best_len or (length == best_len and allow and not best_allow):
            best_len, best_allow = length, allow
    return best_allow if best_len >= 0 else True


def verdict_for_status(status: int | None) -> str | None:
    """RFC 9309 section 2.3.1: what an unreadable robots.txt means.

    Returns None when the body must be parsed (2xx), otherwise
    "allow-all" (4xx) or "disallow-all" (5xx, network error).
    """
    if status is not None and 200 <= status < 300:
        return None
    if status is not None and 400 <= status < 500 and status != 429:
        return "allow-all"
    return "disallow-all"


def _main() -> int:
    import urllib.request

    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    url, token = sys.argv[1], sys.argv[2]
    path = sys.argv[3] if len(sys.argv) > 3 else "/"
    with urllib.request.urlopen(url, timeout=20) as resp:
        robots = parse(resp.read().decode("utf-8", errors="replace"))
    print(f"{token} {path}: {'allow' if is_allowed(robots, token, path) else 'DISALLOW'}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
