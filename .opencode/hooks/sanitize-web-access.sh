#!/usr/bin/env bash
set -euo pipefail

payload="$(</dev/stdin)"

HOOK_INPUT="$payload" python3 - <<'PY'
import ipaddress
import json
import os
import re
import sys
from urllib.parse import unquote, urlparse


def block(reason):
    print(f"Blocked web access: {reason}", file=sys.stderr)
    sys.exit(2)


try:
    data = json.loads(os.environ.get("HOOK_INPUT", "{}"))
except json.JSONDecodeError:
    block("could not parse hook payload")

tool_input = data.get("tool_input") or data.get("toolInput") or {}

text_fields = []
for key in ("url", "uri", "query", "search", "keywords"):
    value = tool_input.get(key)
    if isinstance(value, str):
        text_fields.append((key, value))

if not text_fields:
    block("could not inspect URL/search query before sending it externally")

secret_patterns = [
    (re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"), "private key material"),
    (
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|client[_-]?secret|access[_-]?key|session[_-]?key)\s*[:=]\s*['\"]?[^\s'\"&]{8,}"
        ),
        "secret assignment",
    ),
    (
        re.compile(
            r"\b(?:sk-ant-[A-Za-z0-9_-]{16,}|sk-proj-[A-Za-z0-9_-]{16,}|sk-[A-Za-z0-9_-]{24,}|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,})\b"
        ),
        "known token prefix",
    ),
    (
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
        "JWT-like token",
    ),
    (re.compile(r"\b[A-Fa-f0-9]{48,}\b"), "long hex token"),
    (re.compile(r"\b[A-Za-z0-9+/]{96,}={0,2}\b"), "long base64-like token"),
]

embedded_url_pattern = re.compile(r"https?://[^\s'\"<>]+")
blocked_hostnames = {
    "localhost",
    "metadata.google.internal",
    "169.254.169.254",
}
blocked_suffixes = (".local", ".internal", ".lan")


def validate_no_secrets(label, value):
    decoded = unquote(value)
    for pattern, reason in secret_patterns:
        if pattern.search(decoded):
            block(f"{label} contains {reason}")

    if re.search(r"https?://[^/\s:@]+:[^/\s@]+@", decoded):
        block(f"{label} contains a URL with embedded credentials")


def validate_url(label, raw_url):
    decoded = unquote(raw_url.strip())
    parsed = urlparse(decoded)

    if parsed.scheme not in ("http", "https"):
        block(f"{label} must use http(s), got {parsed.scheme or 'missing scheme'}")

    if not parsed.netloc:
        block(f"{label} is missing a host")

    if parsed.username or parsed.password:
        block(f"{label} contains embedded credentials")

    hostname = (parsed.hostname or "").strip("[]").lower().rstrip(".")
    if not hostname:
        block(f"{label} is missing a hostname")

    if hostname in blocked_hostnames or hostname.endswith(blocked_suffixes):
        block(f"{label} targets a local/private hostname: {hostname}")

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return

    if any((ip.is_private, ip.is_loopback, ip.is_link_local, ip.is_multicast, ip.is_reserved, ip.is_unspecified)):
        block(f"{label} targets a non-public IP address: {hostname}")


for key, value in text_fields:
    validate_no_secrets(key, value)

    if key in ("url", "uri"):
        validate_url(key, value)

    for embedded_url in embedded_url_pattern.findall(value):
        validate_url(f"{key} embedded URL", embedded_url)

sys.exit(0)
PY
