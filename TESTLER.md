# Where the 1.902 comes from

The hero image on this profile claims 1.902 tests across 15 repositories.
This file is that claim, broken down, so you can check it instead of
believing it.

Every number below is a **suite result** — the line a test runner printed at
the end of a run — not a count of `def test_` or `it(` in the source. Those
two disagree, sometimes badly: `mcp-vet` has 243 test functions and 237 test
cases, `mini-creative-toolkit` has 208 functions and 319 cases, because
parametrised tests expand at collection time. An earlier version of the hero
said "1.426 tests" and was wrong in both directions, having been produced by
grepping the tree.

Measured 9 September 2026.

| Repository | Tests | Source of the number |
|---|---:|---|
| [mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit) | 319 | CI log: `319 passed` |
| [buradane](https://github.com/Furkiozknn/buradane) | 278 | 96 backend (CI) + 182 frontend (vitest) |
| [claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence) | 256 | local `pytest`: `256 passed, 2 skipped` |
| [mcp-vet](https://github.com/Furkiozknn/mcp-vet) | 237 | CI log: `237 passed` |
| [ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway) | 150 | CI log: `150 passed, 6 skipped` |
| ajans-os *(private)* | 142 | local `node --test`: `pass 142` |
| turkce-ajanlar *(private)* | 92 | 27 validator + 32 export + 33 format checks |
| [asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit) | 86 | CI log: `86 passed` |
| [ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine) | 72 | CI log: `72 passed` |
| [nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp) | 67 | CI log: `67 passed` |
| [model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness) | 62 | CI log: `62 passed` |
| [prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager) | 58 | CI log: `58 passed` |
| [local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp) | 38 | CI log: `38 passed` |
| [voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp) | 33 | CI log: `33 passed, 2 skipped` |
| [nova-drift](https://github.com/Furkiozknn/nova-drift) | 12 | CI log: `12 passed` (Playwright) |
| **Total** | **1.902** | |

Skipped tests are excluded from every count; a skipped test proves nothing.

## The other two numbers

**15 projects.** Every non-archived repository on the account except this
one, which holds the profile README. Two of them — `ajans-os` and
`turkce-ajanlar` — are still private, for the reason given on the profile.

**408 commits.** `git rev-list --count HEAD`, summed over those same 15
repositories, on 9 September 2026. This repository's own commits are not
included.

## Recheck it yourself

```bash
gh run view --repo Furkiozknn/<repo> --log | grep -E '[0-9]+ passed'
```

If a number here and a number in a repository's own README disagree, the
repository is right and this file is stale. Please open an issue.
