#!/usr/bin/env python3
"""genmedia-mcp - a zero-dependency MCP server for text-to-image and text-to-video.

Four free-tier image providers behind one tool, tried in order until one works,
plus video via Pollinations. Standard library only: no pip install, no npx, no
auto-updating third-party package between you and the network. The whole supply
chain is this file plus providers.py and http_client.py.

Providers (see providers.py for the per-provider notes and signup links):

  cloudflare   10k neurons/day, no card. The most generous free image tier.
  gemini       ~100-500 images/day. Free-tier prompts may be used for training.
  together     free FLUX.1-schnell endpoint.
  pollinations works with NO key at all, and is the only one here doing video.

The default chain is cloudflare -> gemini -> together -> pollinations: best free
tier first, keyless Pollinations last so there is always a floor that works with
no configuration. Unconfigured providers are skipped, not attempted.

Environment:
  IMAGE_PROVIDERS            comma-separated chain override, e.g. "gemini,pollinations"
  POLLINATIONS_KEY           unlocks Pollinations video and its faster image tier
  CLOUDFLARE_ACCOUNT_ID      \\ both needed for the Cloudflare provider
  CLOUDFLARE_API_TOKEN       /
  GEMINI_API_KEY             Google AI Studio key
  TOGETHER_API_KEY           Together AI key
  POLLINATIONS_OUTPUT_DIR    where media is written (default: ./generated-media)
  POLLINATIONS_TIMEOUT       per-request timeout in seconds (default: 300)
  POLLINATIONS_MIN_INTERVAL  override the per-provider request spacing

Run `python3 server.py --selfcheck` to prove every configured provider with one
real call each.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.parse

from http_client import ToolError, http_request
from providers import (
    DEFAULT_CHAIN,
    POLLINATIONS_GEN_HOST,
    POLLINATIONS_SIGNUP,
    REGISTRY,
    _query,
    resolve_chain,
)

SERVER_NAME = "genmedia-mcp"
SERVER_VERSION = "2.0.0"
PROTOCOL_VERSION = "2024-11-05"

# Preview images are inlined so the model can look at what it made. Anything
# bigger is referenced by path only -- a 20 MB base64 blob helps nobody.
MAX_INLINE_PREVIEW_BYTES = 3 * 1024 * 1024


# --------------------------------------------------------------------------
# filesystem safety
# --------------------------------------------------------------------------

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def output_dir() -> str:
    return os.path.abspath(
        os.environ.get("POLLINATIONS_OUTPUT_DIR") or os.path.join(os.getcwd(), "generated-media")
    )


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
    # abspath already collapses '..', so a traversal attempt shows up here as a
    # path that simply is not under root.
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
    return (mimetypes.guess_extension(base) if base else None) or fallback


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


# --------------------------------------------------------------------------
# tools
# --------------------------------------------------------------------------

def tool_generate_image(args: dict) -> list[dict]:
    prompt = (args.get("prompt") or "").strip()
    if not prompt:
        raise ToolError("prompt is required")

    chain = resolve_chain(args.get("provider"))
    params = {
        "model": args.get("model"),
        "width": args.get("width"),
        "height": args.get("height"),
        "seed": args.get("seed"),
        "steps": args.get("steps"),
        "reference_image": args.get("reference_image"),
    }

    failures: list[str] = []
    for provider in chain:
        try:
            payload, mime = provider.generate(prompt, params)
        except ToolError as exc:
            failures.append(f"{provider.name}: {exc}")
            continue

        path = safe_output_path(args.get("output_name"), prompt, extension_for(mime, ".jpg"))
        _write(path, payload)

        lines = [
            f"Image saved to {path}",
            f"  provider: {provider.name}   size: {_human_size(len(payload))} ({mime})",
        ]
        if failures:
            # Say which providers were burned through, so a chain that is quietly
            # falling back every time is visible rather than invisible.
            lines.append("  fell back after: " + "; ".join(failures))

        content: list[dict] = [{"type": "text", "text": "\n".join(lines)}]
        if len(payload) <= MAX_INLINE_PREVIEW_BYTES and mime != "image/svg+xml":
            content.append({"type": "image", "data": base64.b64encode(payload).decode("ascii"), "mimeType": mime})
        return content

    raise ToolError(
        "every provider in the chain failed:\n  " + "\n  ".join(failures)
        + "\n\nRun `python3 server.py --selfcheck` to test each one, or call "
          "list_providers to see what is configured."
    )


def tool_generate_video(args: dict) -> list[dict]:
    prompt = (args.get("prompt") or "").strip()
    if not prompt:
        raise ToolError("prompt is required")

    key = (os.environ.get("POLLINATIONS_KEY") or "").strip()
    if not key:
        raise ToolError(
            "Video needs a Pollinations key: no free provider surveyed offers keyless "
            "text-to-video, at any quality. Registration is free and also speeds up image "
            f"generation -- get a key at {POLLINATIONS_SIGNUP}, set POLLINATIONS_KEY, and "
            "restart the MCP server."
        )

    query = _query({
        "model": args.get("model"),
        "duration": args.get("duration"),
        "aspectRatio": args.get("aspect_ratio"),
        "audio": args.get("audio"),
        "resolution": args.get("resolution"),
        "seed": args.get("seed"),
        "image": args.get("start_image"),
    })
    base = f"{POLLINATIONS_GEN_HOST}/video/{urllib.parse.quote(prompt, safe='')}"
    url = f"{base}?{query}" if query else base

    payload, content_type = http_request(
        url,
        headers={"Authorization": f"Bearer {key}", "Accept": "video/mp4"},
        min_interval=3.0,
    )
    if not content_type.lower().startswith("video/"):
        raise ToolError(
            f"expected a video but got '{content_type or 'unknown'}': "
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


def tool_list_providers(_args: dict) -> list[dict]:
    """What is wired up right now, and what each missing one would need."""
    try:
        chain = [p.name for p in resolve_chain(None)]
    except ToolError as exc:
        chain = [f"(none: {exc})"]

    lines = [f"Active image chain: {' -> '.join(chain)}", ""]
    for name in sorted(REGISTRY):
        provider = REGISTRY[name]
        if provider.configured():
            lines.append(f"  [ready]   {name} -- {provider.notes}")
        else:
            lines.append(f"  [missing] {name} -- set {', '.join(provider.missing())}")
            lines.append(f"            key from: {provider.signup}")
    lines += [
        "",
        f"Default order when IMAGE_PROVIDERS is unset: {' -> '.join(DEFAULT_CHAIN)}",
        "Override with IMAGE_PROVIDERS, or pass provider= to generate_image to pin one.",
        "Video is Pollinations-only and needs POLLINATIONS_KEY.",
    ]
    return [{"type": "text", "text": "\n".join(lines)}]


def tool_list_models(args: dict) -> list[dict]:
    kind = (args.get("kind") or "image").strip().lower()
    if kind not in {"image", "video"}:
        raise ToolError("kind must be 'image' or 'video'")

    # Pollinations' catalogue is public, so this works with no key on any setup.
    payload, _ = http_request(f"{POLLINATIONS_GEN_HOST}/{kind}/models", headers={"Accept": "application/json"})
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ToolError(f"model catalogue was not valid JSON: {exc}") from exc

    entries = parsed.get("data") if isinstance(parsed, dict) else parsed
    if not isinstance(entries, list):
        entries = [parsed]
    names = [
        str(e.get("name") or e.get("id") or e) if isinstance(e, dict) else str(e)
        for e in entries
    ]
    return [{
        "type": "text",
        "text": (
            f"{len(names)} Pollinations {kind} model(s):\n"
            + "\n".join(f"  - {n}" for n in names)
            + "\n\n(Other providers use their own model ids -- see list_providers.)"
        ),
    }]


TOOLS = [
    {
        "name": "generate_image",
        "description": (
            "Generate an image from a text prompt and save it to disk. Tries the configured "
            "provider chain in order until one succeeds; works with no API key at all via "
            "Pollinations. Pass provider= to pin one instead of using the chain."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "What to draw."},
                "provider": {"type": "string", "enum": sorted(REGISTRY), "description": "Pin one provider instead of using the fallback chain."},
                "model": {"type": "string", "description": "Provider-specific model id. Omit for that provider's default."},
                "width": {"type": "integer", "description": "Width in pixels (default 1024)."},
                "height": {"type": "integer", "description": "Height in pixels (default 1024)."},
                "steps": {"type": "integer", "description": "Diffusion steps, where the provider supports it."},
                "seed": {"type": "integer", "description": "Seed for reproducible output."},
                "reference_image": {"type": "string", "description": "Public HTTPS image URL for editing or style reference (Pollinations)."},
                "output_name": {"type": "string", "description": "Filename stem; defaults to a slug of the prompt."},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "generate_video",
        "description": (
            "Generate a short MP4 from a text prompt and save it to disk. Pollinations only, "
            "and requires POLLINATIONS_KEY; registration is free."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "What should happen in the video."},
                "model": {"type": "string", "description": "e.g. veo, wan, seedance-pro, nova-reel."},
                "duration": {"type": "integer", "description": "Length in seconds; allowed values depend on the model."},
                "aspect_ratio": {"type": "string", "description": "e.g. '16:9' or '9:16'."},
                "audio": {"type": "boolean", "description": "Ask for audio, where the model supports it."},
                "resolution": {"type": "string", "description": "Resolution tier, e.g. '720p'."},
                "seed": {"type": "integer", "description": "Seed for reproducible output."},
                "start_image": {"type": "string", "description": "Public HTTPS image URL to use as the first frame."},
                "output_name": {"type": "string", "description": "Filename stem; defaults to a slug of the prompt."},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "list_providers",
        "description": "Show which image providers are configured, the active fallback chain, and what each missing provider needs. Makes no network calls.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_models",
        "description": "List Pollinations' image or video model catalogue. Needs no API key.",
        "inputSchema": {
            "type": "object",
            "properties": {"kind": {"type": "string", "enum": ["image", "video"], "description": "Which catalogue (default: image)."}},
        },
    },
]

HANDLERS = {
    "generate_image": tool_generate_image,
    "generate_video": tool_generate_video,
    "list_providers": tool_list_providers,
    "list_models": tool_list_models,
}


# --------------------------------------------------------------------------
# JSON-RPC / MCP plumbing
# --------------------------------------------------------------------------

def call_tool(name: str, arguments: dict) -> dict:
    """Tool failures come back as isError results, not protocol errors, so the
    model can read what went wrong and adjust instead of the session breaking."""
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
        return {"jsonrpc": "2.0", "id": message_id, "error": {"code": -32601, "message": f"method not found: {method}"}}

    if is_notification:
        return None
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def selfcheck() -> int:
    """Prove each configured provider with one real call. This is the check that
    the environment this server was written in could not run: its egress proxy
    blocks every provider host."""
    print(f"{SERVER_NAME} {SERVER_VERSION} selfcheck")
    print(f"output dir: {output_dir()}\n")

    failures = 0
    for name in sorted(REGISTRY):
        provider = REGISTRY[name]
        if not provider.configured():
            print(f"  SKIP  {name:<12} not configured (set {', '.join(provider.missing())})")
            continue
        started = time.time()
        try:
            payload, mime = provider.generate("a small red circle on a white background", {"width": 512, "height": 512})
            print(f"  OK    {name:<12} {_human_size(len(payload))} {mime} in {time.time() - started:.1f}s")
        except Exception as exc:
            failures += 1
            print(f"  FAIL  {name:<12} {exc}")

    key = (os.environ.get("POLLINATIONS_KEY") or "").strip()
    print(f"\n  {'OK   ' if key else 'SKIP '} video        "
          + ("POLLINATIONS_KEY present (not spending credits on a test clip)"
             if key else f"no POLLINATIONS_KEY -- video unavailable ({POLLINATIONS_SIGNUP})"))
    return 1 if failures else 0


def main() -> int:
    if "--selfcheck" in sys.argv:
        return selfcheck()

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
