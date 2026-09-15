# Where the 2,168 comes from

The hero image on this profile claims 2,168 tests across 16 repositories.
This file is that claim, broken down, so you can check it instead of
believing it.

Every number below is a **suite result** — the line a test runner printed at
the end of a run — not a count of `def test_` or `it(` in the source. Those
two disagree, sometimes badly: `buradane`'s backend has 68 test functions and
96 test cases, `mini-creative-toolkit` has 208 functions and 326 cases,
because parametrised tests expand at collection time. An earlier version of
the hero said "1,426 tests" and was wrong in both directions, having been
produced by grepping the tree.

Measured 15 September 2026, after an audit pass that fixed bugs in 14 of
these repositories and added tests for each fix. That is why several counts
moved since the 14 September measurement.

| Repository | Tests | Δ | Source of the number |
|---|---:|---:|---|
| [mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit) | 326 | +7 | `326 passed, 1 skipped` |
| [buradane](https://github.com/Furkiozknn/buradane) | 324 | +38 | 96 backend (CI log) + 228 frontend (vitest) |
| [mcp-vet](https://github.com/Furkiozknn/mcp-vet) | 289 | +19 | `289 passed` |
| [claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence) | 261 | +2 | `261 passed` |
| [ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway) | 156 | — | CI log: `156 passed`. A local run without the `media` extra gives `150 passed, 6 skipped`. |
| [ajans-os](https://github.com/Furkiozknn/ajans-os) | 142 | — | `node --test`: `pass 142`. Unchanged as a number, but until the glob in `package.json` was quoted, `npm test` silently ran only 137 of them — the end-to-end acceptance run was never among them. |
| [masal](https://github.com/Furkiozknn/masal) | 92 | +3 | `node --test`: `pass 92` |
| [turkce-ajanlar](https://github.com/Furkiozknn/turkce-ajanlar) | 92 | — | 27 validator + 32 export + 33 format checks |
| [asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit) | 86 | — | `86 passed` |
| [nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp) | 80 | +13 | `80 passed` |
| [model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness) | 74 | +12 | `74 passed` |
| [ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine) | 72 | — | `72 passed` |
| [prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager) | 61 | +3 | `61 passed` |
| [local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp) | 50 | +12 | `50 passed, 14 skipped` |
| [voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp) | 35 | +2 | `35 passed, 2 skipped` |
| [nova-drift](https://github.com/Furkiozknn/nova-drift) | 28 | — | `28 passed` (Playwright) |
| **Total** | **2,168** | **+111** | |

Skipped tests are excluded from every count; a skipped test proves nothing.
`local-notes-search-mcp`'s 14 skips are the embedding-model tests, which need
a model download the CI runner does not do — the repository's own README says
so too.

Not in the table: [claude-quota-monitor](https://github.com/Furkiozknn/claude-quota-monitor)
(43 passing tests, but superseded by `claude-code-intelligence` and not
actively developed), [lumen](https://github.com/Furkiozknn/lumen) (a prototype
with a single headless-GDScript harness) and
[godot-2d-sablon](https://github.com/Furkiozknn/godot-2d-sablon) (two starter
templates, no suite). Also not counted: this repository, which holds the
profile README.

## The other two numbers

**16 projects.** The sixteen listed above — everything the profile page
describes. All of them are public.

**622 commits.** `git rev-list --count HEAD`, summed over those same 16
repositories, on 15 September 2026. This repository's own commits are not
included.

This figure was published as 569 for part of that day. The count had been
taken from local clones that had not been fetched, so the merge commits
created on GitHub when pull requests were merged there were missing from
every local history. Re-measured after `git fetch`, with each repository
confirmed level with its remote, the number is 622. It is the kind of error
this file exists to catch, and it is the third one caught so far.

## Recheck it yourself

```bash
gh run view --repo Furkiozknn/<repo> --log | grep -E '[0-9]+ passed'
```

If a number here and a number in a repository's own README disagree, the
repository is right and this file is stale. Please open an issue.
