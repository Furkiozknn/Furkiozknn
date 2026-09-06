#!/usr/bin/env python3
"""pollinations-mcp - a zero-dependency MCP server for text-to-image and text-to-video.

Everything this server can do is in this one file. It talks to the Pollinations
Gen API over plain HTTPS using only the Python standard library: no pip install,
no npx, no auto-updating third-party package sitting between you and the network.

Auth model (see README.md for the full story):

  POLLINATIONS_KEY unset  ->  images only, via the legacy anonymous host
                              image.pollinations.ai. Heavily rate limited and
                              being wound down upstream. Video is refused with
                              an explanatory error rather than a silent failure.
  POLLINATIONS_KEY set    ->  images + video via gen.pollinations.ai. A free
                              key comes from https://enter.pollinations.ai/keys

The model catalogue is public on both paths and needs no key at all.

Environment:
  POLLINATIONS_KEY           optional API key (sk_... or pk_...)
  POLLINATIONS_OUTPUT_DIR    where media is written (default: ./generated-media)
  POLLINATIONS_TIMEOUT       per-request timeout in seconds (default: 300)
  POLLINATIONS_MIN_INTERVAL  seconds to space requests (default: 3 keyed / 15 anon)
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SERVER_NAME = "pollinations-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

GEN_HOST = "https://gen.pollinations.ai"
LEGACY_IMAGE_HOST = "https://image.pollinations.ai"
KEY_SIGNUP_URL = "https://enter.pollinations.ai/keys"

# Preview images are inlined into the tool result so the model can actually look
# at what it made. Anything bigger is referenced by path only -- a 20 MB base64
# blob would blow up the context for no benefit.
MAX_INLINE_PREVIEW_BYTES = 3 * 1024 * 1024

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 3

_last_request_at = 0.0


class ToolError(Exception):
    """A failure worth showing the user verbatim, not a stack trace."""


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

def api_key() -> str | None:
    key = (os.environ.get("POLLINATIONS_KEY") or "").strip()
    return key or None


def output_dir() -> str:
    return os.path.abspath(
        os.environ.get("POLLINATIONS_OUTPUT_DIR") or os.path.join(os.getcwd(), "generated-media")
    )


def request_timeout() -> float:
    return _float_env("POLLINATIONS_TIMEOUT", 300.0)


def min_interval() -> float:
    default = 3.0 if api_key() else 15.0
    return _float_env("POLLINATIONS_MIN_INTERVAL", default)


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value >= 0 else default


# --------------------------------------------------------------------------
# filesystem safety
# --------------------------------------------------------------------------

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def slugify(text: str, limit: int = 48) -> str:
    """Turn a prompt into a filename fragment that cannot escape a directory."""
    cleaned = _UNSAFE.sub("-", text).strip("-._")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned[:limit].strip("-._") or "untitled"


def safe_output_path(name: str | None, prompt: str, extension: str) -> str:
    """Resolve an output path, refusing anything that lands outside output_dir()."""
    root = output_dir()
    stem = slugify(name) if name else f"{slugify(prompt)}-{int(time.time())}"
    if not extension.startswith("."):
        extension = "." + extension
    if stem.lower().endswith(extension.lower()):
        stem = stem[: -len(extension)]

    candidate = os.path.abspath(os.path.join(root, stem + extension))
    # os.path.abspath already collapses '..', so a traversal attempt shows up here
    # as a path that simply is not under root.
    if candidate != root and not candidate.startswith(root + os.sep):
        raise ToolError(f"refusing to write outside {root}")
    return candidate


def extension_for(content_type: str, fallback: str) -> str:
    base = (content_type or "").split(";")[0].strip().lower()
    known = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
    }
    if base in known:
        return known[base]
    guessed = mimetypes.guess_extension(base) if base else None
    return guessed or fallback


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def _throttle() -> None:
    """Space out requests so we do not trip the upstream rate limiter."""
    global _last_request_at
    gap = min_interval()
    if gap <= 0:
        return
    waited = time.time() - _last_request_at
    if _last_request_at and waited < gap:
        time.sleep(gap - waited)
    _last_request_at = time.time()


def _explain_http_error(status: int, body: str) -> str:
    snippet = body.strip()[:400]
    if status == 401:
        return (
            "401 unauthorized: Pollinations rejected the credentials. Set POLLINATIONS_KEY "
            f"to a valid key (free keys: {KEY_SIGNUP_URL}). Details: {snippet}"
        )
    if status == 402:
        return (
            "402 payment required: the key is valid but the account balance or per-key "
            f"budget is exhausted. Details: {snippet}"
        )
    if status == 429:
        return (
            "429 rate limited: too many requests for this tier. Raise "
            "POLLINATIONS_MIN_INTERVAL, or use a key for a higher tier. "
            f"Details: {snippet}"
        )
    return f"HTTP {status} from Pollinations: {snippet}"


def http_get(url: str, *, accept: str, use_key: bool = True) -> tuple[bytes, str]:
    """GET a URL, retrying transient failures. Returns (body, content_type)."""
    headers = {
        "Accept": accept,
        "User-Agent": f"{SERVER_NAME}/{SERVER_VERSION}",
    }
    key = api_key()
    if use_key and key:
        headers["Authorization"] = f"Bearer {key}"

    last_error: str | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        _throttle()
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=request_timeout()) as response:
                return response.read(), response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", "replace")
            except Exception:  # pragma: no cover - body is best-effort only
                pass
            last_error = _explain_http_error(exc.code, body)
            if exc.code not in RETRY_STATUSES or attempt == MAX_ATTEMPTS:
                raise ToolError(last_error) from exc
        except urllib.error.URLError as exc:
            last_error = f"network error reaching {urllib.parse.urlsplit(url).netloc}: {exc.reason}"
            if attempt == MAX_ATTEMPTS:
                raise ToolError(last_error) from exc
        time.sleep(2 ** attempt)

    raise ToolError(last_error or "request failed")


# --------------------------------------------------------------------------
# URL construction
# --------------------------------------------------------------------------

def _query(params: dict) -> str:
    """Drop unset values, normalise booleans, and encode the rest."""
    clean: dict[str, str] = {}
    for name, value in params.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            clean[name] = "true" if value else "false"
        else:
            clean[name] = str(value)
    return urllib.parse.urlencode(clean)


def build_image_url(prompt: str, params: dict) -> str:
    """Keyed requests go to the Gen API; keyless ones to the legacy anonymous host."""
    encoded = urllib.parse.quote(prompt, safe="")
    if api_key():
        base = f"{GEN_HOST}/image/{encoded}"
    else:
        base = f"{LEGACY_IMAGE_HOST}/prompt/{encoded}"
    query = _query(params)
    return f"{base}?{query}" if query else base


def build_video_url(prompt: str, params: dict) -> str:
    encoded = urllib.parse.quote(prompt, safe="")
    query = _query(params)
    base = f"{GEN_HOST}/video/{encoded}"
    return f"{base}?{query}" if query else base


# --------------------------------------------------------------------------
# tools
# --------------------------------------------------------------------------

def _write(path: str, payload: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(payload)


def _human_size(count: int) -> str:
    size = float(count)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def tool_generate_image(args: dict) -> list[dict]:
    prompt = (args.get("prompt") or "").strip()
    if not prompt:
        raise ToolError("prompt is required")

    params = {
        "model": args.get("model"),
        "width": args.get("width"),
        "height": args.get("height"),
        "seed": args.get("seed"),
        "image": args.get("reference_image"),
        "transparent": args.get("transparent"),
    }
    if not api_key():
        # The legacy host understands these two; the Gen API has no equivalent.
        params["nologo"] = "true"
        params["private"] = "true"

    url = build_image_url(prompt, params)
    payload, content_type = http_get(url, accept="image/*")

    if not content_type.lower().startswith("image/"):
        raise ToolError(
            f"expected an image but got '{content_type or 'unknown'}' "
            f"({_human_size(len(payload))}). Body starts: "
            f"{payload[:200].decode('utf-8', 'replace')!r}"
        )

    path = safe_output_path(args.get("output_name"), prompt, extension_for(content_type, ".jpg"))
    _write(path, payload)

    summary = (
        f"Image saved to {path}\n"
        f"  size: {_human_size(len(payload))} ({content_type})\n"
        f"  host: {urllib.parse.urlsplit(url).netloc} ({'keyed' if api_key() else 'anonymous'})"
    )
    content: list[dict] = [{"type": "text", "text": summary}]
    if len(payload) <= MAX_INLINE_PREVIEW_BYTES and content_type.split(";")[0] != "image/svg+xml":
        content.append({
            "type": "image",
            "data": base64.b64encode(payload).decode("ascii"),
            "mimeType": content_type.split(";")[0].strip(),
        })
    return content


def tool_generate_video(args: dict) -> list[dict]:
    prompt = (args.get("prompt") or "").strip()
    if not prompt:
        raise ToolError("prompt is required")
    if not api_key():
        raise ToolError(
            "Video generation needs a Pollinations key: the anonymous legacy host serves "
            "images only. Registration is free and also lifts the image rate limit -- get "
            f"a key at {KEY_SIGNUP_URL}, then set POLLINATIONS_KEY and restart the MCP server."
        )

    params = {
        "model": args.get("model"),
        "duration": args.get("duration"),
        "aspectRatio": args.get("aspect_ratio"),
        "audio": args.get("audio"),
        "resolution": args.get("resolution"),
        "seed": args.get("seed"),
        "image": args.get("start_image"),
    }
    url = build_video_url(prompt, params)
    payload, content_type = http_get(url, accept="video/mp4")

    if not content_type.lower().startswith("video/"):
        raise ToolError(
            f"expected a video but got '{content_type or 'unknown'}'. Body starts: "
            f"{payload[:200].decode('utf-8', 'replace')!r}"
        )

    path = safe_output_path(args.get("output_name"), prompt, extension_for(content_type, ".mp4"))
    _write(path, payload)
    return [{
        "type": "text",
        "text": (
            f"Video saved to {path}\n"
            f"  size: {_human_size(len(payload))} ({content_type})\n"
            f"  model: {args.get('model') or 'veo (server default)'}"
        ),
    }]


def tool_list_models(args: dict) -> list[dict]:
    kind = (args.get("kind") or "image").strip().lower()
    if kind not in {"image", "video"}:
        raise ToolError("kind must be 'image' or 'video'")

    # The catalogue is public on both hosts, so this works with no key at all.
    payload, _ = http_get(f"{GEN_HOST}/{kind}/models", accept="application/json", use_key=True)
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ToolError(f"model catalogue was not valid JSON: {exc}") from exc

    entries = parsed.get("data") if isinstance(parsed, dict) else parsed
    if not isinstance(entries, list):
        entries = [parsed]

    names = []
    for entry in entries:
        if isinstance(entry, dict):
            names.append(str(entry.get("name") or entry.get("id") or entry))
        else:
            names.append(str(entry))

    return [{
        "type": "text",
        "text": f"{len(names)} {kind} model(s):\n" + "\n".join(f"  - {n}" for n in names),
    }]


TOOLS = [
    {
        "name": "generate_image",
        "description": (
            "Generate an image from a text prompt and save it to disk. Works with no API "
            "key (anonymous tier, slow); set POLLINATIONS_KEY for the full model list and "
            "higher rate limits."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "What to draw."},
                "model": {"type": "string", "description": "Model id, e.g. flux, zimage, nanobanana. Omit for the server default."},
                "width": {"type": "integer", "description": "Width in pixels (default 1024)."},
                "height": {"type": "integer", "description": "Height in pixels (default 1024)."},
                "seed": {"type": "integer", "description": "Seed for reproducible output."},
                "reference_image": {"type": "string", "description": "Public HTTPS image URL to edit or use as style reference."},
                "transparent": {"type": "boolean", "description": "Transparent background (gptimage models only)."},
                "output_name": {"type": "string", "description": "Filename stem; defaults to a slug of the prompt."},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "generate_video",
        "description": (
            "Generate a short video (MP4) from a text prompt and save it to disk. Requires "
            "POLLINATIONS_KEY; registration is free."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "What should happen in the video."},
                "model": {"type": "string", "description": "Video model, e.g. veo, wan, seedance-pro. Omit for the server default."},
                "duration": {"type": "integer", "description": "Length in seconds; allowed values depend on the model."},
                "aspect_ratio": {"type": "string", "description": "e.g. '16:9' or '9:16'."},
                "audio": {"type": "boolean", "description": "Ask the model to generate audio, where supported."},
                "resolution": {"type": "string", "description": "Resolution tier advertised by the model, e.g. '720p'."},
                "seed": {"type": "integer", "description": "Seed for reproducible output."},
                "start_image": {"type": "string", "description": "Public HTTPS image URL to use as the first frame."},
                "output_name": {"type": "string", "description": "Filename stem; defaults to a slug of the prompt."},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "list_models",
        "description": "List the image or video models Pollinations currently offers. Needs no API key.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["image", "video"], "description": "Which catalogue to list (default: image)."},
            },
        },
    },
]

HANDLERS = {
    "generate_image": tool_generate_image,
    "generate_video": tool_generate_video,
    "list_models": tool_list_models,
}


# --------------------------------------------------------------------------
# JSON-RPC / MCP plumbing
# --------------------------------------------------------------------------

def call_tool(name: str, arguments: dict) -> dict:
    """Run a tool. Tool failures come back as isError results, not protocol errors,
    so the model can read what went wrong and adjust."""
    handler = HANDLERS.get(name)
    if handler is None:
        return {"content": [{"type": "text", "text": f"unknown tool: {name}"}], "isError": True}
    try:
        return {"content": handler(arguments or {})}
    except ToolError as exc:
        return {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    except Exception as exc:  # pragma: no cover - defensive
        return {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True}


def handle_message(message: dict) -> dict | None:
    """Return a JSON-RPC response, or None for notifications."""
    method = message.get("method")
    message_id = message.get("id")
    is_notification = message_id is None

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }
    elif method in ("notifications/initialized", "initialized"):
        return None
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = message.get("params") or {}
        result = call_tool(params.get("name", ""), params.get("arguments") or {})
    else:
        if is_notification:
            return None
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {"code": -32601, "message": f"method not found: {method}"},
        }

    if is_notification:
        return None
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def main() -> int:
    # stdout is the transport -- anything else printed there corrupts the stream.
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"{SERVER_NAME}: skipping unparseable line: {exc}", file=sys.stderr, flush=True)
            continue

        response = handle_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
