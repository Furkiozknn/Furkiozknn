# `project-meta.json`

Every active repository on this account carries a `project-meta.json` at its
root. It holds the facts about that project that a person would otherwise have
to read the README to learn — what it is, what state it is in, what version,
what it runs on, which images the README actually shows, and how many tests
passed the last time anyone measured.

It exists so that a later tool can answer *"what changed in which project this
week, and what should be said about it"* without parsing prose, and so that the
answer is the same everywhere it is asked.

## The rule the files follow

Mechanical fields are read from the repository itself and from the GitHub API:
description, topics, licence, language, declared version, workflow filenames,
which documentation files exist, which images the README references.

Editorial fields — `key_features`, `technologies`, `category`, `platform`,
`social.headline` — are written by hand and reviewed against the code.

Nothing is generated from a guess. A value that is not known is `null`, not a
plausible-looking string. `tests` is either `null`, or a count together with the
line a test runner printed and the date of that run — a number with no source
does not go in the file.

## Schema

[`project-meta.schema.json`](project-meta.schema.json) — JSON Schema 2020-12.

## One index across every repository

[`derle.py`](derle.py) reads every public repository's `project-meta.json`
through the GitHub API and writes a single `schema/projects.json`, adding the
two facts only the API knows: when each repository was last pushed to, and what
its newest release is.

```bash
python3 schema/derle.py            # writes schema/projects.json
python3 schema/derle.py --stdout   # prints it instead
```

Standard library only, no dependencies. A repository with no `project-meta.json`
is listed under `missing` with the reason — it is never silently dropped, which
is the failure mode that would make the index quietly wrong.

`projects.json` is **not committed**: a checked-in copy goes stale the moment
anything is pushed, and a stale index is worse than no index. Build it when you
need it, or run the *projeler* workflow from the Actions tab, which runs the
same script and uploads the result as an artifact.

## What changed this week, and what to say about it

[`haftalik.py`](haftalik.py) answers the question the metadata exists for.
It reads every repository's `project-meta.json`, then asks the API what
actually happened in a window — commits by conventional-commit type,
releases published — and prints a digest plus one draft post per project
that moved.

```bash
python3 schema/haftalik.py            # last 7 days
python3 schema/haftalik.py --gun 14
python3 schema/haftalik.py --json     # machine-readable
```

Every sentence in a draft comes either from a written field in
`project-meta.json` or from real git/release data in that window. No
adjective and no number is invented: where there is no data, there is no
sentence. The drafts are drafts — they are meant to be read before
anything is posted anywhere.

This is the first real link of `CODE → BUILD → MEDIA → GITHUB → SOCIAL`.
The last hop needs an account that does not exist yet, so nothing is
posted and no account is assumed.

`hafta.json` is not committed, for the same reason `projects.json` is not.

## Fields that matter to a reader

| Field | What it is for |
|---|---|
| `status` | `active`, `prototype` or `archived`. An archived project says so here as well as on GitHub. |
| `version` | The version the project declares, from its manifest or its newest tag. `null` where it declares none. |
| `tests` | The count, the runner line it came from, and when it was measured. |
| `media` | Only assets the README actually shows, as repository-relative paths. |
| `ci.workflows` | The workflow files that actually exist in the repository. |
| `social.primary_link` | Where a reader should be sent: the live deployment where there is one, the repository otherwise. |

## What it deliberately does not contain

Download counts, ratings, user numbers, or any other figure that would have to
be invented to be present.
