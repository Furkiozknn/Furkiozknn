# Where the 5,247 comes from

The hero image on this profile claims 5,247 tests. This file is that claim,
broken down, so you can check it instead of believing it.

Every number below is a **suite result** — the line a test runner printed at
the end of a run — not a count of `def test_` or `it(` in the source. Those
two disagree, sometimes badly, because parametrised tests expand at
collection time: `buradane`'s backend collects 113 functions into 119 cases,
`mini-creative-toolkit` 213 into 327, `ai-job-gateway` 117 into 156. (Those
three lines were themselves stale until 22 September — they had been written
once and never re-collected, which is the same failure this file exists to
prevent, one level up.) An early version of the hero said "1,426 tests" and
was wrong in both directions, having been produced by grepping the tree.

Twenty-eight repositories are public. Twenty-six of them have a suite and are
counted here. The two that are not: `claude-quota-monitor` (43 passing tests,
archived — `claude-code-intelligence` superseded it) and this repository. The
latter does have a suite — 95 tests over the scripts in `schema/`, including
the one that checks this file — and it is left out on purpose: the page that
publishes the total should not be able to raise it.

`godot-2d-sablon` was on that list as "two starter templates, no suite". It
stopped being true on 22 September, when the templates got 21 behavioural
tests over the jump simulation, and the list was not updated — so a
repository with a suite in CI was being left out of a total that exists to be
checkable. It is counted now, which is also why the hub page and this page
finally agree: the hub publishes every non-archived repository's own
`project-meta.json`, this page publishes `schema/meta-source.json`, and until
today nothing compared the two.

`Furkiozknn.github.io` used to be on that list — "generated rather than
written". It is still generated, and that turned out to be the argument for
testing it rather than against: the generator crashed on any repository whose
`summary` was `null`, which is what `.get("summary", "")` returns when the key
is present and null. Every repository happened to have one, so it had never
fired. It now has 37 tests and is counted.

| Repository | Tests | Source of the number | Measured |
|---|---:|---|---|
| [tek-tus-kosu](https://github.com/Furkiozknn/tek-tus-kosu) | 961 | CI log: `=== SONUC: 961 gecti, 0 hata ===` | 22 Sep 2026 |
| [yercekimi-cevir](https://github.com/Furkiozknn/yercekimi-cevir) | 841 | CI log: `841 dogrulama, 0 hata` / `TESTLER GECTI` | 22 Sep 2026 |
| [derin-kazi](https://github.com/Furkiozknn/derin-kazi) | 477 | CI log: 304 unit (`== 304 sinama, 0 hata ==`) + 156 gameplay (`== 156 sinama, 0 hata ==`) + 7 balance (`== 7 sinama, 0 hata ==`) + 10 human-like (`== 10 sinama, 0 hata ==`) | 22 Sep 2026 |
| [buradane](https://github.com/Furkiozknn/buradane) | 347 | 119 backend (CI log: 119 passed) + 228 frontend (vitest) | 22 Sep 2026 |
| [mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit) | 327 | `327 passed` | 22 Sep 2026 |
| [mcp-vet](https://github.com/Furkiozknn/mcp-vet) | 319 | `319 passed` | 22 Sep 2026 |
| [claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence) | 273 | `273 passed` | 22 Sep 2026 |
| [turkce-ajanlar](https://github.com/Furkiozknn/turkce-ajanlar) | 160 | 27 validator + 33 format + 43 browser + 20 team-runner + 19 trigger-collision + 14 boundary + 4 module-type, each from its own printed line | 22 Sep 2026 |
| [ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway) | 156 | CI log: `156 passed` | 15 Sep 2026 |
| [ajans-os](https://github.com/Furkiozknn/ajans-os) | 142 | `node --test`: `pass 142` | 15 Sep 2026 |
| [godot-refcheck](https://github.com/Furkiozknn/godot-refcheck) | 133 | CI log: `=== 133 tests passed ===` | 22 Sep 2026 |
| [repo-ratchet](https://github.com/Furkiozknn/repo-ratchet) | 131 | `131 passed` | 22 Sep 2026 |
| [asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit) | 125 | `125 passed` | 22 Sep 2026 |
| [kanca](https://github.com/Furkiozknn/kanca) | 115 | CI log: `=== 115/115 gecti ===` | 22 Sep 2026 |
| [repo-vet](https://github.com/Furkiozknn/repo-vet) | 103 | CI log: `=== 103 tests passed ===` | 22 Sep 2026 |
| [masal](https://github.com/Furkiozknn/masal) | 92 | `node --test`: `pass 92` | 22 Sep 2026 |
| [ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine) | 80 | 72 suite + 8 cross-repo contract job; CI splits them, so no single line prints 80 | 22 Sep 2026 |
| [nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp) | 80 | `80 passed` | 15 Sep 2026 |
| [model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness) | 74 | `74 passed` | 15 Sep 2026 |
| [local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp) | 64 | `64 passed, 1 warning` | 22 Sep 2026 |
| [prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager) | 61 | `61 passed` | 15 Sep 2026 |
| [mcp-census](https://github.com/Furkiozknn/mcp-census) | 55 | CI log: `55 passed` | 22 Sep 2026 |
| [nova-drift](https://github.com/Furkiozknn/nova-drift) | 38 | `38 passed` (Playwright) | 22 Sep 2026 |
| [Furkiozknn.github.io](https://github.com/Furkiozknn/Furkiozknn.github.io) | 37 | `37 passed` | 22 Sep 2026 |
| [voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp) | 35 | `35 passed, 2 skipped` | 15 Sep 2026 |
| [godot-2d-sablon](https://github.com/Furkiozknn/godot-2d-sablon) | 21 | CI log: `21 passed` | 22 Sep 2026 |
| **Total** | **5,247** | | |

Skipped tests are excluded from every count; a skipped test proves nothing.
`local-notes-search-mcp`'s embedding-model tests used to skip, because the CI
runner did not download the model; its newest run reports `64 passed, 1 warning`
with nothing skipped, so all 64 are counted.

## 22 September: 4,700 → 5,037

Nine repositories moved in a single pass, and the table above is now
**generated** rather than typed. All four of its columns — the count, the
line that printed it, the date it was measured and the repository — live in
[`schema/meta-source.json`](schema/meta-source.json), and
[`schema/testler.py`](schema/testler.py) writes them out to every place the
numbers appear: this table, its total, the heading of this file, the README's
two tables, the five project blurbs that quote a count, the badge, and the
three figures inside `assets/hero.svg`. That is seven surfaces for one
number, and they were kept in step by hand.

The audit already noticed when they drifted — it compares this file's heading
against the metadata sum and the README's table row by row — but it could not
repair anything, and it never looked at *this* file's own table rows, which
could therefore go stale while the heading and the total agreed. `--kontrol`
closes that hole and is a CI gate; `--tazele` is the repair.

| Repository | Was | Now | What changed |
|---|---:|---:|---|
| turkce-ajanlar | 92 | 160 | the composition was stale: seven self-tests print a pass count, and only three were being added up |
| mcp-vet | 289 | 319 | 30 tests for defensive context — a denylist or a comment no longer sets the headline |
| asset-provenance-toolkit | 86 | 125 | a native MP4/QuickTime backend, and the negative control that proves a naive insert breaks the file |
| repo-ratchet | — | 118 | new: the engine that decides which repository to open next |
| buradane | 324 | 334 | the API-contract document is now executable against the schemas it describes |
| repo-vet | 97 | 103 | `--json-out`, and a self-check that the reported count agrees with the exit code |
| ai-workflow-engine | 72 | 80 | eight contract tests that run the *real* neighbouring gateway in-process |
| mcp-census | 44 | 55 | the count is now a time series rather than a single snapshot |
| nova-drift | 28 | 38 | the daily-challenge RNG is tested against the shipped module instead of a copy of it |
| Furkiozknn.github.io | — | 37 | it generates this ecosystem's project directory, and used to crash on a `null` summary |

`Furkiozknn.github.io` and `repo-ratchet` also take the suite count from 23
to 25 and the public repository count from 27 to 28.

Round 2 opened the same day and its first two entries are already here:
`repo-ratchet` 118 → 130 (it had been measuring `<name>-test.js` files as no
tests at all, which is how a repository guarded by eight of them was ranked
first in the round) and `buradane` 334 → 347 (`access` and `operator`, the
two fields round 1's executable contract document had recorded as missing
from every schema).

## What moved, and why

The previous published figure was **2,168 across 16 repositories**, measured
15 September 2026. Five repositories have been published since, all of them
with suites that run headlessly in CI:

| Added | Tests | First green CI run |
|---|---:|---|
| tek-tus-kosu | 853 | 21 Sep 2026 |
| yercekimi-cevir | 841 | 21 Sep 2026 |
| derin-kazi | 460 | 21 Sep 2026 |
| kanca | 115 | 21 Sep 2026 |
| mcp-census | 44 | 21 Sep 2026 |
| | **+2,313** | |

2,168 + 2,313 = 4,481 was the figure published on 21 September. Two of the
sixteen earlier counts have since been re-measured against the newest run that
printed them — `mini-creative-toolkit` 326 → 327, a test that used to skip now
runs, and `local-notes-search-mcp` 50 → 64, its embedding tests no longer skip
— which makes the total **4,496**. `repo-vet` was published on 22 September and
matured against thirty outside repositories the same day, taking its own
suite to **97** and the total to **4,593**. `godot-refcheck` was published later
on 22 September with **73** tests of its own, which made the total **4,666**
across twenty-three suites. Later the same day it grew a repair pass and two
checks for breakage the engine never reports, taking its own suite to **107**
and the total to **4,700**.

Those two were not found by rereading this file. The daily audit goes back to
the run each number came from, re-reads the line in the `Source` column above
and compares: twenty-one of these counts are verified that way every morning.
The other four are composed from more than one run line and are marked as such
rather than checked against a line that does not exist.

The four game repositories are worth a note of their own: the counts are large
because these suites exercise gameplay, not just functions. `yercekimi-cevir`'s
841 checks include playing all 20 rooms to the end screen and confirming a
medal was earned in each. That is a slow suite by design — it is also the only
kind that catches a level becoming unfinishable.

## The other two numbers

**28 public repositories.** Every repository on this account is public except
one unreleased game.

**1,096 commits.** `git rev-list --count HEAD`, summed over those 27
repositories minus this one, on 22 September 2026. This repository's own
commits are not included.

This figure was published as 622 over 16 repositories on 15 September, and as
569 earlier that same day. The 569 had been taken from local clones that had
not been fetched, so the merge commits created on GitHub when pull requests
were merged there were missing from every local history. It is the kind of
error this file exists to catch, and it is the third one caught so far.

The fourth was found on 22 September by running `--olc` rather than
`--kontrol`. `repo-ratchet`'s count was published with `130 passed` as its
source — a line its own CI never wrote, because the workflow ran
`pytest -q` and under `-q` pytest prints the progress dots and no summary at
all. The count was right; its stated source was not in the run, so nobody
could go back and check it, and the offline consistency check stayed green
the whole time. That is the distinction this file turns on: four copies of an
unverifiable number still agree with each other. `-q` is gone from that
workflow and the count is now `131 passed`, a line the run actually prints.

## Recheck it yourself

```bash
gh run view --repo Furkiozknn/<repo> --log | grep -E '[0-9]+ passed|gecti|sinama|dogrulama'
```

Or ask this repository to do it — it reads the same runs and compares them to
what is published here:

```bash
python3 schema/testler.py --kontrol                 # offline: does every surface agree?
DEPO_JETONU=... python3 schema/testler.py --olc     # re-read the run behind each number
DEPO_JETONU=... python3 schema/testler.py --yaz     # ...and write what it measured
```

`--kontrol` needs no token and runs in CI. `--olc` downloads one run log per
repository, which GitHub rate-limits; `--bekleme` spaces the requests out and
`--depo` narrows the pass to one repository at a time.

**The two are not the same question, and the difference is the whole point of
this file.** `--kontrol` asks whether the hero image, the badge, the table and
the totals agree with each other. They can all agree and all be stale — four
copies of one wrong number is still a wrong number. Only `--olc` goes back to
the run. The daily audit (`schema/denetim.py`) does ask the second question,
but it needs a token that can read another repository's run logs, and without
one it used to skip that check in silence: the report said "clean" on days
when the most load-bearing number in this repository had not been looked at at
all. The report now opens with how many counts were actually compared and how
many could not be, and why. A number nobody could check is not a clean number.

The same run hit GitHub's rate limit and the audit died with a Python
traceback — a tool built to say "I could not look" being unable to say
anything at all. A rate limit is now a per-repository result, not a crash: the
run continues, the report names the repositories it could not read, and the
"clean, N repositories" line counts only the ones it actually measured.

Each repository also carries a `project-meta.json` at its root with the same
count, the line it came from and the date — see
[the schema](schema/README.md).

If a number here and a number in a repository's own README disagree, the
repository is right and this file is stale. Please open an issue.
