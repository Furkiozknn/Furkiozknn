# How the account is operated

`docs/ECOSYSTEM.md` describes what the visitor sees. This page describes the
machinery behind it: what runs on its own, what checks what, what is still
done by hand, and why. It started as the **System ×4 audit of 25 September
2026**; the numbers in the audit sections are from that day and say so.

## The control loop

```
27 repositories ──► denetim.yml (daily 05:00)  ──► "Ekosistem denetimi" issue
                    ├─ red CI on default branches, workflows GitHub disabled
                    ├─ release chain: tag ─► release ─► PyPI
                    ├─ metadata vs live repository, links, install commands
                    ├─ published test counts vs the run that printed them  [DEPO_JETONU]
                    └─ workflow + supply-chain policy (schema/politika.py)
                 ──► sayilar.yml (daily 05:40) ──► profile counts, committed  [DEPO_JETONU]
                 ──► vitrin.yml  (daily 05:17) ──► README "Recently", committed
                 ──► yenile.yml  (weekly)      ──► project-meta.json per repo [DEPO_JETONU]
human ──► merge · tag · release · settings · secrets   (never automated)
```

Everything that can go stale is generated or checked; everything with an
external effect (merge, tag, publish, settings) waits for a person.

## Policy (`schema/politika.py`)

One file holds the rules every repository's workflows are held to. The same
function runs against a local clone (`--kok`, `--depo`), inside this
repository's CI (`--depo . --kati`, so the repository that sets the rules
obeys them first) and in the daily audit over the GitHub API.

| Rule | Level | Why |
|---|---|---|
| `boru` — test output piped (`pytest \| tee`) without `pipefail` | FAIL | GitHub's default shell is `bash -e` without pipefail: the pipe returns `tee`'s 0 and a failing suite shows green |
| `enjeksiyon` — `${{ github.event.* }}` / `head_ref` text inside `run:` | FAIL | anyone who opens a PR controls that text; the shell runs it |
| `tetik` — `pull_request_target` / `workflow_run` | FAIL if it checks out the PR's code, else WARN | secrets + untrusted code in one job is the "pwn request" |
| `yaml` — a workflow that does not parse | FAIL | a broken file must not read as "no findings" |
| `sure` — a job without `timeout-minutes` | WARN | a hung test runs for GitHub's default 6 hours |
| `pin` — third-party action on a tag, not a commit SHA | WARN | a tag can be moved under you; a SHA cannot |
| `izin` — no `permissions` | WARN | the token then gets whatever the repository default is |
| `dependabot` / `grup` — updates missing or ungrouped | WARN | ungrouped means one PR per package: 36 open on 25 Sep |
| `kilit` — a lockfile no Dependabot entry covers | WARN | its dependencies never get updated |

Deliberately **not** rules: `inputs.*` in `run:` (only people with write
access can dispatch), `continue-on-error` (used on purpose), and a shared
reusable publish workflow — PyPI Trusted Publishing does not work from a
reusable workflow, so centralising the twelve `yayinla.yml` copies would
break every release. Drift between the copies is the thing to watch instead.

## System ×4 audit — 25 September 2026

Scope: the 27 active public repositories, audited as they will be **after**
the open Claude PRs merge (each default branch plus its PRs, merged in the
documented order; all 27 chains merged without a conflict).

**A. Repository health.** 27 repositories, 26 with a test suite. Every one
has README and LICENSE; `project-meta.json` everywhere. CHANGELOG is missing
where there is nothing to version (five games, profile, directory site,
ajans-os). No CODEOWNERS — one maintainer, no value yet.

**B. CI/CD.** 56 workflows, 128 jobs. Clean on the dangerous axes: no
`pull_request_target`, no `workflow_run`, no event text in a shell, every
workflow sets `permissions`, and every place a test is piped into `tee`
sets `pipefail` (five of them — fixed during Phase 3). The gap was
operational: **108 of 128 jobs had no timeout.**

**C. Security.** The code-level findings of Phase 3 (symlink secret read,
DNS rebinding, YAML/gzip bombs, workflow injection, path traversal, the
`bash -c` bypass) are fixed with regression tests. Supply chain: 62 uses of
third-party actions on moving tags (`astral-sh/setup-uv@v7`,
`pypa/gh-action-pypi-publish@release/v1`) — including the jobs that build and
publish the PyPI artifact.

**D. Dependencies.** 16 Dependabot configurations, **none grouped**, all
weekly → 36 open Dependabot PRs. 11 repositories with none, which is why
`actions/checkout` ran as v4, v5, v6 and v7 at once. buradane's
`frontend/package-lock.json` and `backend/uv.lock` were covered by nothing.

**E. Tests.** pytest exits 5 on "no tests collected"; the Godot suites go
through `tests/kapi.sh`, which fails on `SCRIPT ERROR` and on a lower-than-
expected count; Playwright fails on zero tests. The published count of 26
repositories **could not be checked against CI** on 25 Sep: that comparison
needs `DEPO_JETONU`.

**F. Releases.** All 13 PyPI publishers use OIDC Trusted Publishing, no
token anywhere, and every one of them refuses to build when the tag differs
from the `pyproject.toml` version (mcp-census also checks `__version__` and
that CHANGELOG has a section for the tag). Two tags exist without a PyPI
release (mcp-census, repo-vet v0.1.0): the Trusted Publisher is not
registered yet.

**G. Automation.** The audit, the counts, the "Recently" section and the
metadata refresh are automated. Three of them are degraded without
`DEPO_JETONU` (see *Single points of failure*).

**H. Documentation.** README and LICENSE in all 27; SECURITY.md in 18,
CHANGELOG in 19, issue templates in 14; 23 repositories share one banner
system. Whether each README answers *install / quick start / configure /
test* was not audited here — that is a reading job, not a grep.

**I. Profile.** v3: short README, a Currently line, one link line,
descriptions that fit a pinned card (≤100 characters, enforced by
`about/uygula.py`). Pins, bio and website are set by hand — no API.

**J. Pages.** Four Godot games have a working web export and a publish job;
none is live because Pages is not enabled in their settings. tek-tus-kosu's
last "Yapi" run is red for exactly that reason (the export succeeded;
`configure-pages` failed).

**K. PyPI.** 13 projects, one workflow shape: `yayinla.yml`, job `yayinla`,
environment `pypi`, `id-token: write`, triggered by `v*` tags. Note:
prompt-template-manager publishes as **`ptm-cli`**.

**L. Observability.** One issue carries every finding, deduplicated by a
fingerprint; each automated commit says which run made it. New: workflows
GitHub disabled after 60 days of inactivity are reported (before, a stopped
schedule was invisible — no run, so no red run).

**M. Technical debt.** Action versions drift until Dependabot runs
everywhere; `pip install pytest` unpinned in three small repositories.

**N. Duplication.** 12 near-identical publish workflows (two families,
93–99 % and ~62 % similar) — kept separate on purpose (see *Policy*).
The Godot log gate (`tests/kapi.sh`) exists in four games.

**O. Manual operations** — see the table below.

**P. Single points of failure.**
1. `DEPO_JETONU` — one missing secret turns off test-count verification,
   the automatic count sync and the metadata self-repair.
2. A single approver for every merge: 46 Claude PRs and 36 Dependabot PRs
   were waiting on one person on 25 Sep. Grouping and stacking cut the
   count; the approval itself stays human.
3. Post-merge follow-ups lived in one session's notes until `sayilar.yml`.

**Q. Highest-leverage changes** (in the order they were made):
policy engine in the daily audit (every repo, every day, and the rule can't
silently regress) → grouped monthly Dependabot everywhere (36 PRs → at most
one per ecosystem per month, and paired actions move together) → measured
timeouts on every job → SHA-pinned third-party actions → automatic count
sync.

## Manual operations

| # | Operation | How it works today | Automation | Status |
|---|---|---|---|---|
| 1 | Merge Dependabot PRs | one PR per action per week, merged one by one | `groups` + monthly: one PR per ecosystem | rolling out: one commit per repository on its open PR |
| 2 | Keep upload/download-artifact in step | remembered by a person | same group → same PR | done |
| 3 | Update profile counts after a merge | hand-edited in 7 places | `sayilar.yml` measures and commits | needs `DEPO_JETONU` |
| 4 | Check a published count is real | nobody could, for 26 repos | `denetim.py` reads the run log | needs `DEPO_JETONU` |
| 5 | Notice a hung job | 6 h of runner time, then red | measured `timeout-minutes` everywhere | rolling out: one commit per repository on its open PR |
| 6 | Notice a workflow GitHub switched off | not noticed | daily audit reports `disabled_inactivity` | done |
| 7 | Keep new workflows to the rules | code review | policy in the daily audit + this repo's CI | done |
| 8 | Keep action versions current | never | Dependabot in all 27 repositories | rolling out: one commit per repository on its open PR |
| 9 | Know a tag reached PyPI | by hand | daily audit (tag → release → PyPI) | existing |
| 10 | Apply About texts | `about/uygula.py --uygula` by hand | a workflow with an admin-scoped token | proposed |
| 11 | Register Trusted Publishers | pypi.org UI, 13 times | none possible — values listed below | manual, one-time |
| 12 | Enable Pages | repository settings, 4 times | none possible without an admin token | manual, one-time |
| 13 | Tag a release on the right commit | a command typed by hand | readiness check that prints the exact command from the merge SHA | proposed |
| 14 | Simulate a merge chain for conflicts | a script run by hand | same script in `yenile.yml` | proposed |
| 15 | Social preview images | upload by hand | none possible — no API | manual, one-time |

### Trusted Publisher values (pypi.org → Publishing → Add a pending publisher)

Owner `Furkiozknn`, workflow `yayinla.yml`, environment `pypi`, for:
ai-job-gateway, ai-workflow-engine, asset-provenance-toolkit,
claude-code-intelligence, local-notes-search-mcp, mcp-census, mcp-vet,
mini-creative-toolkit, model-comparison-harness, nvidia-nim-mcp,
repo-vet, voice-io-mcp — each under its repository name — and
prompt-template-manager under the PyPI name **`ptm-cli`**.

### `DEPO_JETONU`

A fine-grained personal access token, stored as a secret in this repository
only. Repository access: all repositories. Permissions: **Actions: Read**
(run logs), **Contents: Read and write** (the weekly metadata refresh),
**Dependabot alerts: Read**. Rotation: when it expires, the daily audit says
"bakilamadi" instead of pretending to be clean.

## Rollback

| Change | Undo |
|---|---|
| Policy check in the audit | revert the commit; the audit runs as before |
| `sayilar.yml` commit | `git revert` the bot commit; `testler.py --kontrol` still gates |
| Dependabot grouping | revert the file; Dependabot returns to one PR per package |
| Timeouts | raise the number, or delete the line |
| SHA pins | replace the SHA with the tag; Dependabot keeps SHA and comment in step |
