# Where the 4,496 comes from

The hero image on this profile claims 4,496 tests. This file is that claim,
broken down, so you can check it instead of believing it.

Every number below is a **suite result** — the line a test runner printed at
the end of a run — not a count of `def test_` or `it(` in the source. Those
two disagree, sometimes badly: `buradane`'s backend has 68 test functions and
96 test cases, `mini-creative-toolkit` has 208 functions and 327 cases,
because parametrised tests expand at collection time. `ai-job-gateway` has 9
test functions and 156 cases. An early version of the hero said "1,426 tests"
and was wrong in both directions, having been produced by grepping the tree.

Twenty-four repositories are public. Twenty-one of them have a suite and are
counted here. The three that are not: `godot-2d-sablon` (two starter
templates, no suite), `claude-quota-monitor` (43 passing tests, archived —
`claude-code-intelligence` superseded it) and this repository, which holds the
profile README.

| Repository | Tests | Source of the number | Measured |
|---|---:|---|---|
| [tek-tus-kosu](https://github.com/Furkiozknn/tek-tus-kosu) | 853 | CI log: `=== SONUC: 853 gecti, 0 hata ===` | 22 Sep 2026 |
| [yercekimi-cevir](https://github.com/Furkiozknn/yercekimi-cevir) | 841 | CI log: `841 dogrulama, 0 hata` → `TESTLER GECTI` | 22 Sep 2026 |
| [derin-kazi](https://github.com/Furkiozknn/derin-kazi) | 460 | CI log, two jobs: `== 304 sinama, 0 hata ==` (unit) + `== 156 sinama, 0 hata ==` (gameplay) | 22 Sep 2026 |
| [mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit) | 327 | `327 passed` | 22 Sep 2026 |
| [buradane](https://github.com/Furkiozknn/buradane) | 324 | 96 backend (CI log) + 228 frontend (vitest) | 15 Sep 2026 |
| [mcp-vet](https://github.com/Furkiozknn/mcp-vet) | 289 | `289 passed` | 15 Sep 2026 |
| [claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence) | 261 | `261 passed` | 15 Sep 2026 |
| [ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway) | 156 | CI log: `156 passed`. A local run without the `media` extra gives `150 passed, 6 skipped`. | 15 Sep 2026 |
| [ajans-os](https://github.com/Furkiozknn/ajans-os) | 142 | `node --test`: `pass 142` | 15 Sep 2026 |
| [kanca](https://github.com/Furkiozknn/kanca) | 115 | CI log: `=== 115/115 gecti ===` | 22 Sep 2026 |
| [masal](https://github.com/Furkiozknn/masal) | 92 | `node --test`: `pass 92` | 15 Sep 2026 |
| [turkce-ajanlar](https://github.com/Furkiozknn/turkce-ajanlar) | 92 | 27 validator + 32 export + 33 format checks | 15 Sep 2026 |
| [asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit) | 86 | `86 passed` | 15 Sep 2026 |
| [nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp) | 80 | `80 passed` | 15 Sep 2026 |
| [model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness) | 74 | `74 passed` | 15 Sep 2026 |
| [ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine) | 72 | `72 passed` | 15 Sep 2026 |
| [prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager) | 61 | `61 passed` | 15 Sep 2026 |
| [local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp) | 64 | `64 passed, 1 warning` | 22 Sep 2026 |
| [mcp-census](https://github.com/Furkiozknn/mcp-census) | 44 | CI log: `44 passed in 0.13s` | 21 Sep 2026 |
| [voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp) | 35 | `35 passed, 2 skipped` | 15 Sep 2026 |
| [nova-drift](https://github.com/Furkiozknn/nova-drift) | 28 | `28 passed` (Playwright) | 15 Sep 2026 |
| **Total** | **4,496** | | |

Skipped tests are excluded from every count; a skipped test proves nothing.
`local-notes-search-mcp`'s embedding-model tests used to skip, because the CI
runner did not download the model; its newest run reports `64 passed, 1 warning`
with nothing skipped, so all 64 are counted.

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
— which makes the current total **4,496**.

Those two were not found by rereading this file. The daily audit now goes back
to the run each number came from, re-reads the line in the `Source` column
above and compares: fourteen of these counts are verified that way every
morning. The rest are composed from more than one run line and are marked as
such rather than checked against a line that does not exist.

The four game repositories are worth a note of their own: the counts are large
because these suites exercise gameplay, not just functions. `yercekimi-cevir`'s
841 checks include playing all 20 rooms to the end screen and confirming a
medal was earned in each. That is a slow suite by design — it is also the only
kind that catches a level becoming unfinishable.

## The other two numbers

**24 public repositories.** Every repository on this account is public except
one unreleased game.

**848 commits.** `git rev-list --count HEAD`, summed over those 24
repositories minus this one, on 22 September 2026. This repository's own
commits are not included.

This figure was published as 622 over 16 repositories on 15 September, and as
569 earlier that same day. The 569 had been taken from local clones that had
not been fetched, so the merge commits created on GitHub when pull requests
were merged there were missing from every local history. It is the kind of
error this file exists to catch, and it is the third one caught so far.

## Recheck it yourself

```bash
gh run view --repo Furkiozknn/<repo> --log | grep -E '[0-9]+ passed|gecti|sinama|dogrulama'
```

Each repository also carries a `project-meta.json` at its root with the same
count, the line it came from and the date — see
[the schema](schema/README.md).

If a number here and a number in a repository's own README disagree, the
repository is right and this file is stale. Please open an issue.
