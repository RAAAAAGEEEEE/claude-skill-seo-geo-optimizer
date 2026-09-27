#!/usr/bin/env python3
"""Credentials for the audit scripts: read from environment variables or
from a file path, never from the command line (visible in the process list
and in shell history), never written to a report or a log.

    key = envkeys.secret("PAGESPEED_API_KEY")        # None if unset
    text = envkeys.redact(text, [key])                # before printing/saving

Stdlib only.
"""

from __future__ import annotations

import os
from pathlib import Path


def secret(env_name: str) -> str | None:
    value = os.environ.get(env_name, "").strip()
    return value or None


def secret_file(env_name: str) -> Path | None:
    """Path to a credentials file named by an environment variable, if it exists."""
    value = os.environ.get(env_name, "").strip()
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_file() else None


def redact(text: str, secrets: list[str | None]) -> str:
    for s in secrets:
        if s and len(s) >= 4:
            text = text.replace(s, "[REDACTED]")
    return text


def redact_obj(obj, secrets: list[str | None]):
    """Recursively redact strings in a JSON-like structure."""
    if isinstance(obj, str):
        return redact(obj, secrets)
    if isinstance(obj, list):
        return [redact_obj(x, secrets) for x in obj]
    if isinstance(obj, tuple):
        return tuple(redact_obj(x, secrets) for x in obj)
    if isinstance(obj, dict):
        return {k: redact_obj(v, secrets) for k, v in obj.items()}
    return obj
