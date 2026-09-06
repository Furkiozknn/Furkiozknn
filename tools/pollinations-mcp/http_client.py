"""Shared HTTP plumbing: retries, per-provider throttling, and readable errors.

Standard library only. Kept separate from the providers so a provider adapter is
just "build a request, read a response" with no networking policy mixed in.
"""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "pollinations-mcp/2.0.0"
RETRY_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
MAX_ATTEMPTS = 3

# Throttling is per host, so a Cloudflare call is never delayed by the 15-second
# spacing the anonymous Pollinations tier needs.
_last_call_at: dict[str, float] = {}


class ToolError(Exception):
    """A failure worth showing the user verbatim, not a stack trace."""


def env_value(name: str) -> str | None:
    """Read an env var, treating blank and unexpanded placeholders as unset.

    Claude Code expands ${VAR:-default} in .mcp.json, but a config that drops
    the ":-" leaves the literal "${VAR}" text in place when the variable is
    unset. Without this guard that string would be sent as an API key and come
    back as an unexplained 401, so treat it as absent instead.
    """
    raw = (os.environ.get(name) or "").strip()
    if not raw or (raw.startswith("${") and raw.endswith("}")):
        return None
    return raw


def request_timeout() -> float:
    raw = os.environ.get("POLLINATIONS_TIMEOUT")
    if raw and raw.strip():
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
    return 300.0


def _throttle(host: str, min_interval: float) -> None:
    override = os.environ.get("POLLINATIONS_MIN_INTERVAL")
    if override and override.strip():
        try:
            min_interval = max(0.0, float(override))
        except ValueError:
            pass
    if min_interval <= 0:
        return
    previous = _last_call_at.get(host, 0.0)
    if previous:
        waited = time.time() - previous
        if waited < min_interval:
            time.sleep(min_interval - waited)
    _last_call_at[host] = time.time()


def explain_http_error(status: int, body: str, host: str) -> str:
    snippet = " ".join(body.split())[:400]
    if status in (401, 403):
        return (
            f"{status} from {host}: credentials missing, invalid, or lacking the right "
            f"permission. Details: {snippet}"
        )
    if status == 402:
        return f"402 from {host}: the account authenticated but its balance or budget is spent. Details: {snippet}"
    if status == 429:
        return (
            f"429 from {host}: free-tier rate limit hit. Wait, raise POLLINATIONS_MIN_INTERVAL, "
            f"or let the chain fall through to another provider. Details: {snippet}"
        )
    return f"HTTP {status} from {host}: {snippet}"


def http_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict | None = None,
    body: bytes | None = None,
    min_interval: float = 0.0,
) -> tuple[bytes, str]:
    """Perform one HTTP call, retrying transient failures. Returns (body, content_type)."""
    host = urllib.parse.urlsplit(url).netloc
    all_headers = {"User-Agent": USER_AGENT}
    all_headers.update(headers or {})

    last_error: str | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        _throttle(host, min_interval)
        request = urllib.request.Request(url, data=body, headers=all_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=request_timeout()) as response:
                return response.read(), response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", "replace")
            except Exception:  # pragma: no cover - body is best-effort only
                pass
            last_error = explain_http_error(exc.code, detail, host)
            if exc.code not in RETRY_STATUSES or attempt == MAX_ATTEMPTS:
                raise ToolError(last_error) from exc
        except urllib.error.URLError as exc:
            last_error = f"network error reaching {host}: {exc.reason}"
            if attempt == MAX_ATTEMPTS:
                raise ToolError(last_error) from exc
        time.sleep(2 ** attempt)

    raise ToolError(last_error or "request failed")
