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
import importlib.util
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
SEMA = KOK / "schema" / "project-meta.schema.json"


def _sema_denetleyici():
    """schema/dogrula.py icindeki sema yorumlayicisini odunc alir.

    Ayni kurali iki yerde yazmamak icin: dosyanin kendisi tek kaynak.
    Bulunamazsa dogrulama atlanir ve bu ciktida yazili olur.
    """
    yol = KOK / "schema" / "dogrula.py"
    if not yol.is_file():
        return None, None
    spec = importlib.util.spec_from_file_location("meta_dogrula", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._sema_dogrula, json.loads(SEMA.read_text(encoding="utf-8"))


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

    denetle, sema = _sema_denetleyici()
    projects, missing, bozuk = [], [], []
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
        if denetle is not None:
            # latest_release/pushed_at gibi API alanlari semada yok; sema
            # denetimi dosyanin kendi alanlari uzerinde yapilir.
            cikarilan = {k: v for k, v in meta.items()
                         if k not in ("pushed_at", "default_branch",
                                      "open_issues", "latest_release")}
            hatalar = []
            denetle(cikarilan, sema, "", hatalar)
            if hatalar:
                bozuk.append({"id": meta["id"], "hatalar": hatalar})
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
        "schema_violations": bozuk,
        "schema_checked": denetle is not None,
    }
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if args.stdout:
        sys.stdout.write(text)
    else:
        out = KOK / "schema" / "projects.json"
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"{out}: {len(projects)} proje, {len(missing)} eksik, "
              f"{len(bozuk)} sema ihlali"
              + ("" if denetle is not None else "  (dogrula.py yok: sema denetimi atlandi)"))
        for b in bozuk:
            print(f"  {b['id']}:")
            for h in b["hatalar"]:
                print(f"    {h}")
    if bozuk:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
