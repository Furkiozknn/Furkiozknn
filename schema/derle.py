#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect every repository's project-meta.json into one index.

Each repository carries its own project-meta.json; this reads them all and
writes a single `schema/projects.json`, plus the two live facts that only the
API knows: when the repository was last pushed to, and what its newest release
is.

Nothing is cached in git that can go stale silently: the output carries the
timestamp it was built at, and any repository whose project-meta.json is
missing is listed by name under `missing` rather than quietly dropped.

    python3 schema/derle.py                    # writes schema/projects.json
    python3 schema/derle.py --stdout           # prints instead of writing
    GITHUB_TOKEN=... python3 schema/derle.py   # higher rate limit

Only the standard library is used.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWNER = "Furkiozknn"
API = "https://api.github.com"
KOK = Path(__file__).resolve().parent.parent


def _get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "project-meta-collector",
    })
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _repos():
    out, page = [], 1
    while True:
        batch = _get(f"{API}/users/{OWNER}/repos?per_page=100&page={page}&sort=pushed")
        if not batch:
            break
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def _meta(name, branch):
    try:
        blob = _get(f"{API}/repos/{OWNER}/{name}/contents/project-meta.json?ref={branch}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    return json.loads(base64.b64decode(blob["content"]).decode("utf-8"))


def _release(name):
    try:
        r = _get(f"{API}/repos/{OWNER}/{name}/releases/latest")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    return {"tag": r["tag_name"], "name": r["name"], "published_at": r["published_at"],
            "url": r["html_url"], "assets": len(r.get("assets", []))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    projects, missing = [], []
    for r in _repos():
        if r.get("fork"):
            continue
        meta = _meta(r["name"], r["default_branch"])
        if meta is None:
            missing.append({"id": r["name"], "archived": r["archived"],
                            "reason": "no project-meta.json on the default branch"})
            continue
        meta["pushed_at"] = r["pushed_at"]
        meta["default_branch"] = r["default_branch"]
        meta["open_issues"] = r["open_issues_count"]
        meta["latest_release"] = _release(r["name"])
        projects.append(meta)

    projects.sort(key=lambda m: m["pushed_at"], reverse=True)
    doc = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owner": OWNER,
        "count": len(projects),
        "note": "Built from each repository's own project-meta.json. A repository with no "
                "such file is listed under 'missing', not silently dropped.",
        "projects": projects,
        "missing": missing,
    }
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if args.stdout:
        sys.stdout.write(text)
    else:
        out = KOK / "schema" / "projects.json"
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"{out}: {len(projects)} proje, {len(missing)} eksik")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
