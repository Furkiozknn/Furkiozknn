#!/usr/bin/env python3
"""Apply the GitHub repository metadata this session could not.

The Claude Code GitHub integration can push code and open/merge PRs, but its
token lacks the `administration` permission: creating repositories and
editing descriptions/topics both returned 403 ("Resource not accessible by
integration"), and the session proxy additionally refuses non-repo-scoped
endpoints. So this script exists: run it once with a personal access token
that has `repo` (classic) or `Administration: write` + `Metadata` (fine-grained).

    export GITHUB_TOKEN=ghp_...
    python3 research/lab/apply-github-metadata.py            # dry run
    python3 research/lab/apply-github-metadata.py --apply

Then push the three waiting repos:

    for r in ai-cost-estimator ai-repo-scaffold webhook-sink; do
      git -C ../$r remote add origin https://github.com/Furkiozknn/$r.git
      git -C ../$r push -u origin main
    done
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

OWNER = "Furkiozknn"

CREATE = {
    "ai-cost-estimator": "Estimate the cost of a batch of AI generation jobs (image/video/3D/audio/TTS) across hosted providers, from a bundled, sourced pricing table.",
    "ai-repo-scaffold": "Generate a new Python repo skeleton matching the Furkiozknn AI-creative-tools ecosystem's conventions - pyproject.toml, CI, README, LICENSE, tests - in one command.",
    "webhook-sink": "A tiny zero-dependency local HTTP server that accepts and logs any webhook POST - for testing ai-job-gateway's webhook delivery and retry behaviour against something real instead of a mock.",
}

METADATA = {
    "mini-creative-toolkit": ("Local media operations for MCP clients - images, video and audio. CPU-first, no paid APIs; exactly one hosted tool, isolated and disclosed. 23 tools, `mct` CLI.",
        ["mcp", "model-context-protocol", "claude-code", "python", "image-processing", "video-processing", "ffmpeg", "pillow", "opencv", "cli", "local-first"]),
    "mcp-vet": ("Trust and security auditor for MCP servers: registry provenance, capability and credential inventory, data-flow and injection analysis, version diffs. Evidence over scores; never says 'safe'.",
        ["mcp", "mcp-security", "model-context-protocol", "security", "security-audit", "supply-chain-security", "claude-code", "agent-skills", "python", "cli"]),
    "ai-job-gateway": ("Provider-agnostic, self-hostable reference implementation of the submit/poll/webhook async job contract used by fal.ai, BFL and RunPod - with idempotency keys, signed webhooks and a Python client.",
        ["async-jobs", "webhooks", "fastapi", "python", "reference-implementation", "generative-ai", "job-queue", "api"]),
    "prompt-template-manager": ("Versioned, git-diffable prompt/pipeline templates for generative-AI requests, with a sandboxed strict renderer and a CLI.",
        ["prompt-engineering", "prompt-templates", "jinja2", "yaml", "cli", "python", "generative-ai"]),
    "model-comparison-harness": ("Run the same request against multiple generative-model backends concurrently and compare latency, success and results side by side - table, JSON or CSV.",
        ["evaluation", "benchmarking", "model-comparison", "generative-ai", "asyncio", "cli", "python"]),
    "asset-provenance-toolkit": ("Embed and extract generation provenance (capability, provider, params, job id) directly in PNG and JPEG files - container-level, never re-encoding pixels.",
        ["provenance", "metadata", "png", "jpeg", "ai-generated-content", "c2pa", "python", "cli"]),
    "ai-workflow-engine": ("A small DAG orchestrator that chains ai-job-gateway-compatible jobs (generate -> upscale -> lip-sync) from a YAML pipeline, with sandboxed templating and parse-time validation.",
        ["dag", "workflow-engine", "orchestration", "yaml", "pipeline", "generative-ai", "python", "cli"]),
    "local-notes-search-mcp": (None,
        ["mcp", "model-context-protocol", "semantic-search", "sqlite-vec", "fastembed", "local-first", "claude-code", "python"]),
    "voice-io-mcp": (None,
        ["mcp", "model-context-protocol", "text-to-speech", "speech-to-text", "whisper", "kokoro", "groq", "claude-code", "python"]),
    "ai-cost-estimator": (None, ["pricing", "cost-estimation", "generative-ai", "cli", "python"]),
    "ai-repo-scaffold": (None, ["scaffolding", "project-template", "python", "cli", "uv"]),
    "webhook-sink": (None, ["webhooks", "testing", "http-server", "python", "zero-dependency"]),
}


def call(method: str, path: str, body: dict | None, token: str) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"https://api.github.com{path}", data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def main() -> int:
    apply = "--apply" in sys.argv
    token = os.environ.get("GITHUB_TOKEN", "")
    if apply and not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 2
    for name, desc in CREATE.items():
        print(f"create  {OWNER}/{name}")
        if apply:
            code, out = call("POST", "/user/repos", {"name": name, "description": desc, "private": False, "auto_init": False, "has_wiki": False}, token)
            print(f"        -> {code} {out.get('html_url') or out.get('message')}")
    for name, (desc, topics) in METADATA.items():
        print(f"update  {OWNER}/{name}: topics={len(topics)}{' + description' if desc else ''}")
        if apply:
            if desc:
                code, out = call("PATCH", f"/repos/{OWNER}/{name}", {"description": desc}, token)
                print(f"        description -> {code} {out.get('message', 'ok')}")
            code, out = call("PUT", f"/repos/{OWNER}/{name}/topics", {"names": topics}, token)
            print(f"        topics      -> {code} {out.get('message', 'ok')}")
    if not apply:
        print("\ndry run - re-run with --apply to make the changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
