"""Image-generation providers, each a thin adapter over one free-tier HTTP API.

Adding a provider means adding a class here and one entry to REGISTRY. Nothing
else in the server knows how many providers exist, so a chain of four costs the
same to reason about as a chain of one.

Every provider returns (image_bytes, mime_type) or raises ToolError. None of
them import anything outside the standard library.

Verification status matters here and is recorded honestly: the Pollinations
request shape was read from its published APIDOCS.md, but the Cloudflare,
Gemini and Together shapes could not be checked against their vendor docs from
the environment this was written in (the egress proxy blocks those hosts). Run
`python3 server.py --selfcheck` on an unrestricted machine to prove each one
with a real call before trusting it.
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.parse

from http_client import ToolError, env_value, http_request

# --------------------------------------------------------------------------

POLLINATIONS_GEN_HOST = "https://gen.pollinations.ai"
POLLINATIONS_LEGACY_HOST = "https://image.pollinations.ai"
POLLINATIONS_SIGNUP = "https://enter.pollinations.ai/keys"


def _query(params: dict) -> str:
    """Drop unset values, normalise booleans, and encode the rest."""
    clean: dict[str, str] = {}
    for name, value in params.items():
        if value is None or value == "":
            continue
        clean[name] = "true" if value is True else "false" if value is False else str(value)
    return urllib.parse.urlencode(clean)


def _decode_b64(data: str, provider: str) -> bytes:
    try:
        return base64.b64decode(data, validate=True)
    except Exception as exc:
        raise ToolError(f"{provider} returned base64 that would not decode: {exc}") from exc


def _as_json(payload: bytes, provider: str) -> dict:
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ToolError(
            f"{provider} returned a non-JSON body ({len(payload)} bytes): "
            f"{payload[:200].decode('utf-8', 'replace')!r}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ToolError(f"{provider} returned JSON that was not an object: {type(parsed).__name__}")
    return parsed


# --------------------------------------------------------------------------


class Provider:
    """One free-tier image API."""

    name = ""
    needs: tuple[str, ...] = ()
    signup = ""
    notes = ""
    # Requests/second this tier tolerates, used to space calls client-side.
    min_interval = 1.0

    def configured(self) -> bool:
        return all(env_value(var) for var in self.needs)

    def missing(self) -> list[str]:
        return [var for var in self.needs if not env_value(var)]

    def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        raise NotImplementedError


class Pollinations(Provider):
    """Keyless on the legacy host; the full catalogue and video with a free key."""

    name = "pollinations"
    needs = ()
    signup = POLLINATIONS_SIGNUP
    notes = "works with no key at all (slow); a free key unlocks video and ~5x the rate"

    def key(self) -> str | None:
        return env_value("POLLINATIONS_KEY")

    @property
    def min_interval(self) -> float:  # type: ignore[override]
        return 3.0 if self.key() else 15.0

    def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        query = {
            "model": params.get("model"),
            "width": params.get("width"),
            "height": params.get("height"),
            "seed": params.get("seed"),
            "image": params.get("reference_image"),
        }
        key = self.key()
        headers = {"Accept": "image/*"}
        if key:
            base = f"{POLLINATIONS_GEN_HOST}/image/{urllib.parse.quote(prompt, safe='')}"
            headers["Authorization"] = f"Bearer {key}"
        else:
            base = f"{POLLINATIONS_LEGACY_HOST}/prompt/{urllib.parse.quote(prompt, safe='')}"
            # Only the legacy host understands these.
            query["nologo"] = "true"
            query["private"] = "true"

        encoded = _query(query)
        url = f"{base}?{encoded}" if encoded else base
        payload, content_type = http_request(url, headers=headers, min_interval=self.min_interval)

        if not content_type.lower().startswith("image/"):
            raise ToolError(
                f"pollinations returned '{content_type or 'unknown'}' instead of an image: "
                f"{payload[:200].decode('utf-8', 'replace')!r}"
            )
        return payload, content_type.split(";")[0].strip()


class Cloudflare(Provider):
    """Workers AI. 10,000 neurons/day free on a card-free account -- roughly
    2,000 small FLUX images, which is the most generous free image tier found."""

    name = "cloudflare"
    needs = ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN")
    signup = "https://dash.cloudflare.com/profile/api-tokens (needs the Workers AI permission)"
    notes = "10k neurons/day, no credit card; default model @cf/black-forest-labs/flux-1-schnell"
    min_interval = 0.0

    def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        account = env_value("CLOUDFLARE_ACCOUNT_ID")
        token = env_value("CLOUDFLARE_API_TOKEN")
        model = params.get("model") or "@cf/black-forest-labs/flux-1-schnell"

        body: dict = {"prompt": prompt}
        if params.get("steps"):
            body["steps"] = params["steps"]
        if params.get("seed") is not None:
            body["seed"] = params["seed"]

        url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}"
        payload, content_type = http_request(
            url,
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            body=json.dumps(body).encode(),
            min_interval=self.min_interval,
        )

        # Some Workers AI image models stream raw PNG; flux-1-schnell wraps
        # base64 in the standard Cloudflare envelope. Handle both.
        if content_type.lower().startswith("image/"):
            return payload, content_type.split(";")[0].strip()

        parsed = _as_json(payload, "cloudflare")
        if parsed.get("success") is False:
            errors = parsed.get("errors") or parsed.get("messages") or parsed
            raise ToolError(f"cloudflare rejected the request: {json.dumps(errors)[:300]}")

        result = parsed.get("result")
        image = result.get("image") if isinstance(result, dict) else None
        if not image:
            raise ToolError(
                f"cloudflare response had no result.image field: {json.dumps(parsed)[:300]}"
            )
        return _decode_b64(image, "cloudflare"), "image/jpeg"


class Gemini(Provider):
    """Google's Nano Banana (gemini-2.5-flash-image). Free tier, no card, but
    Google may train on free-tier submissions -- do not send anything private."""

    name = "gemini"
    needs = ("GEMINI_API_KEY",)
    signup = "https://aistudio.google.com/apikey"
    notes = "free tier ~100-500 images/day; free-tier prompts may be used for training"
    min_interval = 1.0

    def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        key = env_value("GEMINI_API_KEY")
        model = params.get("model") or "gemini-2.5-flash-image"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        body = {"contents": [{"parts": [{"text": prompt}]}]}

        payload, _ = http_request(
            url,
            method="POST",
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            body=json.dumps(body).encode(),
            min_interval=self.min_interval,
        )
        parsed = _as_json(payload, "gemini")

        candidates = parsed.get("candidates") or []
        for candidate in candidates:
            parts = ((candidate or {}).get("content") or {}).get("parts") or []
            for part in parts:
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                    return _decode_b64(inline["data"], "gemini"), mime

        # A refusal comes back as a normal 200 with text instead of an image,
        # so surface whatever the model said rather than a generic parse error.
        text = ""
        for candidate in candidates:
            for part in ((candidate or {}).get("content") or {}).get("parts") or []:
                if part.get("text"):
                    text += part["text"]
        raise ToolError(
            f"gemini returned no image. {('Model said: ' + text[:300]) if text else json.dumps(parsed)[:300]}"
        )


class OpenAICompatibleImages(Provider):
    """Any provider exposing OpenAI's POST /v1/images/generations.

    Adding one is three lines: subclass, set base_url/default_model/needs, and
    register it. Together and NVIDIA differ only in those fields.
    """

    base_url = ""
    default_model = ""
    key_env = ""
    min_interval = 1.0

    def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        body = {
            "model": params.get("model") or self.default_model,
            "prompt": prompt,
            "width": params.get("width") or 1024,
            "height": params.get("height") or 1024,
            "n": 1,
            "response_format": "b64_json",
        }
        if params.get("steps"):
            body["steps"] = params["steps"]
        if params.get("seed") is not None:
            body["seed"] = params["seed"]

        payload, _ = http_request(
            f"{self.base_url}/images/generations",
            method="POST",
            headers={
                "Authorization": f"Bearer {env_value(self.key_env)}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body=json.dumps(body).encode(),
            min_interval=self.min_interval,
        )
        parsed = _as_json(payload, self.name)

        entries = parsed.get("data") or []
        if entries:
            entry = entries[0]
            if entry.get("b64_json"):
                return _decode_b64(entry["b64_json"], self.name), "image/jpeg"
            # Some OpenAI-compatible hosts ignore response_format and hand back a
            # URL instead, so follow it rather than failing on a valid response.
            if entry.get("url"):
                image, content_type = http_request(entry["url"], headers={"Accept": "image/*"})
                if not content_type.lower().startswith("image/"):
                    raise ToolError(f"{self.name} result URL served '{content_type}', not an image")
                return image, content_type.split(";")[0].strip()

        raise ToolError(
            f"{self.name} response had no data[0].b64_json or .url: {json.dumps(parsed)[:300]}"
        )


class Together(OpenAICompatibleImages):
    """Together AI's FLUX.1-schnell-Free endpoint."""

    name = "together"
    needs = ("TOGETHER_API_KEY",)
    key_env = "TOGETHER_API_KEY"
    base_url = "https://api.together.xyz/v1"
    default_model = "black-forest-labs/FLUX.1-schnell-Free"
    signup = "https://api.together.ai/settings/api-keys"
    notes = "free FLUX.1-schnell endpoint; no card, but the free tier has been promo-based"


class NvidiaNIM(OpenAICompatibleImages):
    """NVIDIA's API catalogue. Free developer credits that do not expire, no card."""

    name = "nvidia"
    needs = ("NVIDIA_API_KEY",)
    key_env = "NVIDIA_API_KEY"
    base_url = "https://integrate.api.nvidia.com/v1"
    default_model = "black-forest-labs/flux.1-schnell"
    signup = "https://build.nvidia.com (NVIDIA Developer Program, email only)"
    notes = "~5,000 free credits that do not expire, ~40 RPM, no credit card"


class BFL(Provider):
    """Black Forest Labs -- the people who make FLUX. Free FLUX.2 [dev] and
    FLUX Kontext [dev], rate limited, no card.

    Unlike the others this API is asynchronous: POST returns a polling_url, and
    the finished image lives behind a delivery URL that expires ten minutes
    after it becomes ready.
    """

    name = "bfl"
    needs = ("BFL_API_KEY",)
    signup = "https://dashboard.bfl.ai/get-started"
    notes = "free flux-2-dev and flux-kontext-dev, rate limited, no card; async polling"
    min_interval = 1.0

    poll_interval = 1.5
    max_polls = 60

    def generate(self, prompt: str, params: dict) -> tuple[bytes, str]:
        key = env_value("BFL_API_KEY")
        headers = {"x-key": key, "Content-Type": "application/json", "Accept": "application/json"}
        model = params.get("model") or "flux-2-dev"

        body: dict = {"prompt": prompt}
        if params.get("width"):
            body["width"] = params["width"]
        if params.get("height"):
            body["height"] = params["height"]
        if params.get("seed") is not None:
            body["seed"] = params["seed"]
        if params.get("reference_image"):
            body["input_image"] = params["reference_image"]

        payload, _ = http_request(
            f"https://api.bfl.ai/v1/{model}",
            method="POST",
            headers=headers,
            body=json.dumps(body).encode(),
            min_interval=self.min_interval,
        )
        submitted = _as_json(payload, "bfl")
        polling_url = submitted.get("polling_url")
        if not polling_url:
            raise ToolError(f"bfl accepted nothing to poll: {json.dumps(submitted)[:300]}")

        for _ in range(self.max_polls):
            payload, _ = http_request(polling_url, headers=headers)
            state = _as_json(payload, "bfl")
            status = (state.get("status") or "").lower()

            if status == "ready":
                sample = (state.get("result") or {}).get("sample")
                if not sample:
                    raise ToolError(f"bfl reported Ready with no result.sample: {json.dumps(state)[:300]}")
                # Delivery URLs expire ten minutes after Ready, so fetch immediately.
                image, content_type = http_request(sample, headers={"Accept": "image/*"})
                if not content_type.lower().startswith("image/"):
                    raise ToolError(f"bfl delivery URL served '{content_type}', not an image")
                return image, content_type.split(";")[0].strip()

            if status in ("error", "failed"):
                raise ToolError(f"bfl failed: {json.dumps(state)[:300]}")
            if status in ("request moderated", "content moderated"):
                raise ToolError(f"bfl refused the prompt on moderation grounds (status: {status})")

            time.sleep(self.poll_interval)

        raise ToolError(
            f"bfl did not finish within {self.max_polls * self.poll_interval:.0f}s "
            f"(last status: {status or 'unknown'})"
        )


REGISTRY: dict[str, Provider] = {
    provider.name: provider
    for provider in (Cloudflare(), Gemini(), NvidiaNIM(), BFL(), Together(), Pollinations())
}

# Best free tier first, keyless Pollinations last so the chain always has a
# floor that works with no configuration at all.
DEFAULT_CHAIN = ("cloudflare", "gemini", "nvidia", "bfl", "together", "pollinations")


def resolve_chain(requested: str | None = None) -> list[Provider]:
    """Work out which providers to try, in order.

    A single named provider is used alone and is allowed to fail loudly -- if you
    asked for Cloudflare you want to know Cloudflare broke, not get a silent
    Pollinations image instead.
    """
    if requested:
        name = requested.strip().lower()
        if name not in REGISTRY:
            raise ToolError(
                f"unknown provider '{requested}'. Available: {', '.join(sorted(REGISTRY))}"
            )
        return [REGISTRY[name]]

    raw = (os.environ.get("IMAGE_PROVIDERS") or "").strip()
    names = [n.strip().lower() for n in raw.split(",") if n.strip()] if raw else list(DEFAULT_CHAIN)

    chain = [REGISTRY[n] for n in names if n in REGISTRY and REGISTRY[n].configured()]
    if not chain:
        raise ToolError(
            "no image provider is configured. The zero-setup option is Pollinations "
            "(no key needed) -- check IMAGE_PROVIDERS if you have narrowed the chain."
        )
    return chain
