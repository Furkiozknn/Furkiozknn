---
title: Your README is a promise
date: 2026-09-25
summary: Checking the install commands, badges, links and releases of 29 well-known repositories over the GitHub API, without cloning anything.
repo: repo-vet
---

# Your README is a promise

*25 September 2026 · [repo-vet](https://github.com/Furkiozknn/repo-vet)*

A README makes promises that can be checked. `pip install thing` promises the
package exists. A CI badge promises the workflow exists and has run. A relative
link promises the file is in the tree. A version in `pyproject.toml` promises a
tag. These go stale quietly, because the only way to notice is to try them, and
nobody tries their own README a second time.

I found this out on my own account first. One of my repositories opened with
`uv tool install ptm-cli`, for a package I had never published. So the first
command a new visitor ran failed with *"ptm-cli was not found in the package
registry"*. Every test in that repository passed, because none of them tested
the README.

[repo-vet](https://github.com/Furkiozknn/repo-vet) tries these promises over
the GitHub API. It doesn't clone anything, and it runs six checks:

- **install**: package names in fenced code blocks, checked against PyPI and npm
- **links**: relative links and images, checked against the file tree
- **badges**: workflow badges point at a workflow that exists and has run
- **release**: the version the manifest declares was actually tagged and released
- **web**: outbound links, where only 404 and 410 count
- **pages**: a GitHub Pages site that is dead, or live but not linked anywhere

## Twenty-nine repositories that disagree with each other

A checker that cries wolf gets switched off. So before release I ran it on 29
public repositories chosen because they differ from each other:

- Python: requests, flask, httpx, pytest, poetry, uv, ruff, fastapi and others
- JavaScript and TypeScript: express, axios, vite, svelte, prettier
- Rust and Go: ripgrep, bat, clap, cobra, fzf, bubbletea
- documentation repositories with no code at all
- `torvalds/linux`, whose file tree is too large for GitHub to return in one piece

That run produced four findings, one of them an error. I checked each by hand:

| Repository | Finding |
|---|---|
| `axios/axios` | The CI badge points at `ci.yml`. The workflow is `run-ci.yml`, so the badge shows *"no status"* rather than red. |
| `tiangolo/fastapi` | The README links to `tutorial/`, which 404s on GitHub. It works on the docs site, so this is a warning and a judgement call for the authors. |
| `sindresorhus/awesome` | A GitHub Pages site is live, but the repository's homepage field is empty. |
| `Furkiozknn/repo-vet` | It declared 0.1.0 and hadn't tagged it yet. That was my own repository. |

The axios one is the most typical. Rename a workflow and nothing goes red. The
badge just stops meaning anything, and nobody looks closely at a grey badge.

## Three rules those repositories proved wrong

The corpus changed the tool more than the tool found problems in the corpus.
Three rules I thought were obvious did not survive it:

- **"The newest tag should have a release."** The tags API returns tags in no
  guaranteed order. It gave `v0.1.16` as fastapi's newest tag, and
  `wincolor-0.1.6` as ripgrep's. The release check now starts from the version
  the manifest declares, which needs no ordering.
- **"A declared version should be tagged."** Between releases, a project
  declares the version it is working towards: flask says `3.2.0.dev`. That's
  normal work in progress, not a defect.
- **"A relative link must exist."** For fastapi, `tutorial/` is a route on the
  documentation site. A missing link with a file extension is still an error.
  One shaped like a route is now a warning.

Five more findings were plain bugs in the checker:

- A registry that couldn't be reached was read as "not published".
- A truncated file tree was read as missing files. `torvalds/linux` returns
  71,638 paths plus a flag saying there are more.
- Commands inside code examples were treated as promises.
- Percent-encoded paths were reported as missing.
- A rate limit was reported as "no such repository".

Each of these is now a named test.

## The tool's own README

While preparing this post I ran the same kind of check on repo-vet's own
README. It said the corpus had thirty repositories; the file has twenty-nine.
The file's header also listed a private repository, an archived one and one
that doesn't exist, and none of those was ever in it. All three are fixed now.
I'm mentioning it because it's the whole argument in one example: I wrote the
tool, and my own README still drifted.

## Try it

It isn't on PyPI yet, and the README says so rather than showing a
`pip install` that would fail:

```sh
uvx --from git+https://github.com/Furkiozknn/repo-vet repo-vet OWNER/NAME
```

In CI:

```yaml
- uses: Furkiozknn/repo-vet@main
  with:
    fail-on: error
```

It uses only the standard library and makes no network calls in its tests. It
also never fixes anything automatically or opens issues: the output is a list
of observations with the evidence attached, and what to do about each one is up
to you. If it reports something in your repository that isn't wrong,
[tell me](https://github.com/Furkiozknn/repo-vet/issues). That's how the three
rules above changed.
