# `project-meta.json`

Every active repository on this account carries a `project-meta.json` at its
root. It holds the facts about that project that a person would otherwise have
to read the README to learn — what it is, what state it is in, what version,
what it runs on, which images the README actually shows, and how many tests
passed the last time anyone measured.

It exists so that a later tool can answer *"what changed in which project this
week, and what should be said about it"* without parsing prose, and so that the
answer is the same everywhere it is asked.

## Producing the files

[`uret.py`](uret.py) writes every repository's `project-meta.json`. It reads
the mechanical half from the clone and the GitHub API, and the editorial half
from [`meta-source.json`](meta-source.json) — which lives here, in the
repository, rather than on one machine.

```bash
python3 schema/uret.py --kok /where/the/clones/are
```

That placement is the point. The editorial fields are the half nobody can
regenerate from code: what a project's three or four real selling points are,
which test count came from which runner line. Keeping them on a single disk
made the metadata layer only as durable as that disk. A fresh clone and a
token now rebuild the whole layer.

A repository with no entry in `meta-source.json` is skipped and named at the
end, with exit code 1 — so a new project cannot quietly fall out of the layer.

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

## Checking the files against the schema — and against the repository

[`dogrula.py`](dogrula.py) validates a `project-meta.json` two ways, because
schema conformance alone is not much of a guarantee:

1. **Against the schema** — required fields, types, closed object shapes,
   the `status` enum. The subset of JSON Schema these files use is
   interpreted directly, so no `jsonschema` install is needed.
2. **Against the repository** — whether what the file *claims* is actually
   there: every path under `media` and `docs` resolves to a real file,
   `ci.workflows` matches the workflow files on disk, `tests` carries a
   source and a date alongside its count, `id` matches the directory.

```bash
python3 schema/dogrula.py ../some-repo
python3 schema/dogrula.py --kok /path/to/all/clones
```

Exit code 1 on the first error, so it works as a gate. The second check is
the one that earns its keep: adding a workflow to four repositories left
their `ci.workflows` lists a step behind, and this is what said so.

`derle.py` runs the schema half over everything it collects and reports
`schema_violations`; it cannot run the filesystem half, because it reads
through the API and never has the working tree.

## Checking the account against itself, every day

`dogrula.py` needs the clones, which means it needs the one machine that has
them. [`denetim.py`](denetim.py) asks a narrower question that needs nothing
but a token, so GitHub can ask it on its own:

```bash
GITHUB_TOKEN=... python3 schema/denetim.py
```

For every non-fork repository it checks whether `project-meta.json` is on the
default branch, whether the repository has an entry in `meta-source.json`,
whether the mechanical half of the metadata still matches the live repository
(description, topics, licence, homepage, archived state, workflow filenames),
whether LICENSE and README are where the file says they are, whether the
description and topics are empty, and whether the newest finished run of each
of the repository's **own** workflows is red.

It also checks this profile's own headline numbers, which are the numbers
most likely to rot quietly. `TESTLER.md` names one canonical figure in its
title; the audit sums `tests.count` across every non-archived repository and
compares. It also checks that the README repeats that same figure, that the
public-repository count on the page matches the live one, and that **every
row of the project table carries the test count its own metadata reports**.
The per-row check is the one that earns its keep: a total can stay right
while two rows drift in opposite directions, and a reader looks at the row,
not the total. Adding seven tests to one game is enough to make the page
wrong, and nobody would notice by reading.

Two things are deliberately out of scope. Runs GitHub manages itself — the
Dependabot updater, default-setup CodeQL — are not the repository's CI, so a
permanently red dependency bump or a run left queued by archiving is not
reported every morning. And Dependabot alerts are not readable across
repositories with a workflow token; reporting "clean" for something it cannot
see would be worse than saying nothing.

It fixes nothing and commits nothing. It exits 0 even when it finds
something, because one repository's missing licence should not turn another
repository's badge red.

The *denetim* workflow runs it daily at 05:00 UTC and keeps a single
*Ekosistem denetimi* issue: it comments when the **set** of findings changes,
stays quiet when the same findings are still open, and closes the issue with a
note when everything clears. A repository that has no entry in
`meta-source.json` gets a ready-to-paste skeleton in that comment, with the
mechanical fields filled and the editorial ones left `null` — a new project is
onboarded by writing four fields, not by remembering that the layer exists.

## Taking a published number back to the run that printed it

The whole claim of this profile is that its numbers can be checked. Until
now that check happened once, by hand, and the result was written down in
two places — the README row and `project-meta.json`. Two copies of a stale
number agree with each other perfectly.

`tests.source` already records *which line* a count came from. The audit now
uses it as an instruction rather than a footnote: it finds the newest
successful `ci.yml` run, downloads its log, looks for that exact line, and
reads the number out again. Fourteen of the twenty-two suites are verified
this way every morning. The rest compose their count from more than one run
line — `derin-kazi` adds a unit job to a gameplay job, `buradane` adds a
backend suite to a frontend one — and those are marked unverifiable rather
than measured against a line that does not exist.

Its first run found two published numbers that had gone stale:
`local-notes-search-mcp` 50 → 64 and `mini-creative-toolkit` 326 → 327,
which moved the profile total from 4,481 to 4,496. Neither would have been
caught by rereading the page.

Three more checks were added at the same time, and all four are silent
today — each one speaks exactly when something real happens:

| Check | Fires when |
|---|---|
| Newest tag without a Release | a tag was pushed and the release never followed |
| Tag without the matching PyPI version | the publish workflow failed or never ran |
| `status: active`, no push in six months | the page says a project is live when it is not |
| Pages answering at the conventional URL while `homepage` is null | a site went live and nobody wrote it down |
| A README code block installs a distribution that is not on PyPI | the first command a visitor copies would fail |

The last one was written after it happened: `prompt-template-manager`'s
install section opened with `uv tool install ptm-cli`, and `ptm-cli` has
not been published, so a first-time visitor's first command died with
*"ptm-cli was not found in the package registry"*. Only fenced code blocks
are checked — a sentence mentioning a command is discussing it, not asking
anyone to run it.

Reading run logs needs `Actions: Read`, so the count check runs only when
`DEPO_JETONU` is set. Without it the audit stays quiet about counts rather
than pretending they were verified.

## Fixing the drift, not just finding it

The audit can see that a `project-meta.json` no longer matches its
repository, but it cannot fix it: regenerating needs each repository's
working tree, which used to mean one particular Windows machine being
switched on.

The *yenile* workflow closes that. Every Monday at 04:30 UTC it clones all
of them (treeless, no credentials needed — they are public), runs `uret.py`
over the lot, puts the result through `dogrula.py`, and prints the diff.
What happens next depends on one secret:

- **No `DEPO_JETONU`** — it stops there and writes what *would* change into
  the run summary. Useful on its own: a second drift detector that shows the
  exact diff rather than a description of it.
- **With `DEPO_JETONU`** — a fine-grained token with `Contents: Read and
  write` on the repositories — each changed file is committed to its own
  repository and the layer repairs itself with nobody watching.

Only `project-meta.json` is ever staged, nothing is pushed if the validator
fails, archived repositories are skipped because they reject pushes, and
there is no force push anywhere. The same token, given `Dependabot alerts:
Read`, also turns on the one check the daily audit is otherwise blind to;
`denetim.json` reports how many repositories it actually managed to read
rather than claiming a clean bill it could not have seen.

## The gates in front of all of this

These scripts write into twenty-four repositories now, which makes an
untested change to them an expensive one. Three gates run on every push to
this repository ([`ci.yml`](../.github/workflows/ci.yml)):

1. [`test_schema.py`](test_schema.py) — 41 tests, standard library only.
   Most of them come from a bug that actually happened, and each says which
   one at the top: a `"private": true` flag that silently dropped `masal`'s
   version, a plugin manifest that was never read so `turkce-ajanlar` looked
   versionless, four `ci.workflows` lists left a step behind. Nothing here
   tests a failure that has never occurred.
2. This repository's own `project-meta.json`, through both halves of
   `dogrula.py`.
3. Every workflow YAML, parsed. Not a formality: an invalid workflow file
   fails on GitHub with no jobs, no log and no annotation to explain it.

And one more gate stands specifically in front of the automatic refresh.
The schema cannot object to a value disappearing, because most fields are
nullable — which is exactly how the `masal` version loss got through
everything. [`koruma.py`](koruma.py) applies a one-way rule: **a full value
going empty is suspicious, an empty one filling in is not.** `yenile.yml`
puts every file through it, and also checks the blast radius — if more
repositories than the threshold (8 by default) change at once, it touches
none of them, because that is almost always a bug in the generator rather
than twenty-four simultaneous real drifts.

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

Each draft carries the project's hero image URL alongside it, resolved from
the `media.hero` path the metadata already holds — a post without a picture
tends not to get made.

Every sentence in a draft comes either from a written field in
`project-meta.json` or from real git/release data in that window. No
adjective and no number is invented: where there is no data, there is no
sentence. The drafts are drafts — they are meant to be read before
anything is posted anywhere.

It runs itself. The `haftalik` workflow fires every Monday at 06:00 UTC: it
collects the index, validates it against the schema, asks what moved in the
last seven days, and — **only if something moved** — posts the digest as a
comment on a single *Haftalik ozet* issue. One issue with a comment history,
not fifty-two issues a year, and nothing is committed: a processed summary
goes stale on the next push, and a weekly bot commit would inflate the
contribution graph with work nobody did.

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
