# SkillSpector — Scanning All 57 Installed Skills

**Tool:** [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) v2.11.0 (commit `7805bb9`), Apache 2.0.
A security scanner for AI agent skills: 71 vulnerability patterns across 17 categories, two-stage
(fast static analysis + optional LLM semantic evaluation), part of NVIDIA's Verified Skills pipeline.
**Run:** static stage only (`--no-llm`), every skill scanned individually.
**Date:** September 2026.

This is the tool the [MCP security section](G_adjacent_free_tiers_and_tooling.md#4-mcp-security-and-the-ecosystem)
of the previous pass was describing the need for — someone else already built the skill-side half.

---

## 1. Install

Needs Python 3.12+; the box has 3.11, so `uv` supplies the interpreter:

```bash
git clone --depth 1 https://github.com/NVIDIA/skillspector
uv tool install --python 3.12 ./skillspector
```

Clean install, one executable, no manual dependency work.

## 2. Headline numbers

57 skills, 187 findings.

| Severity | Skills |
|---|---:|
| CRITICAL | 3 |
| HIGH | 1 |
| MEDIUM | 16 |
| LOW | 37 |

Four skills were rated **`DO_NOT_INSTALL`**: `docx` (100/100), `pptx` (100/100), `xlsx` (92/100),
`task-observer` (59/100).

Full table: [`skillspector/scan-results.tsv`](skillspector/scan-results.tsv).

## 3. Every HIGH finding, traced to its source

Each one was opened and read rather than taken on the scanner's word. **All of them are false positives.**

### 3.1 `rm -f ../out.docx` → "Tool Misuse: Tool Parameter Abuse" + "Chaining Abuse" (conf 0.85 / 0.75)

The flagged line is the documented OOXML repack step:

```bash
(cd unpacked && rm -f ../out.pptx && zip -Xr ../out.pptx .)  # rm first or deleted parts survive
```

The skill's own inline comment explains why the `rm` is there: `zip` updates an existing archive in
place, so without deleting first, parts you removed survive into the output. It deletes **its own
output file**. The scanner reads `&& rm -` as capability chaining.

### 3.2 `﻿` → "Prompt Injection: Hidden Instructions" ×3 (conf 0.6)

The entire finding is one character: **U+FEFF, a UTF-8 byte-order mark**, at line 1 of three vendor
ECMA OOXML schema files (`opc-contentTypes.xsd`, `opc-coreProperties.xsd`, `opc-relationships.xsd`).
A BOM in a standards-body XSD is being reported as invisible text carrying malicious directives.

### 3.3 `os.environ.copy()` → "Data Exfiltration: Env Variable Harvesting" (conf 0.6)

```python
def get_soffice_env() -> dict:
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"
```

This builds the environment for launching LibreOffice headless. Nothing is transmitted anywhere.
Any `subprocess` call that needs to add one variable to the inherited environment matches this rule.

### 3.4 `scripts/clean.py unpacked/` → "analysis-evasion" ×3 (conf 1.0)

One row of a markdown capability table — *"Delete slides, media, and rels no longer referenced"* —
flagged three times because three lines of `SKILL.md` reference it. Confidence 1.0 on a documented
cleanup script.

### 3.5 `task-observer`

- *"analysis-evasion"* on the line **"Bundle manifest: this skill consists of `SKILL.md` plus the three…"**.
  A bundle manifest declaration read as evasion, at confidence 1.0.
- *"Rogue Agent: Self-Modification"* on the phrase **"update skill"** in prose describing the weekly
  review. This is the one finding with any substance — `task-observer` genuinely does propose changes
  to other skills — but that is its documented, opt-in purpose, and the review presents a summary for
  approval. Covert self-modification it is not.

## 4. Verdict on the tool

**In static-only mode, precision on this corpus was 0.** Every HIGH finding across four
`DO_NOT_INSTALL` skills was a false positive, and three of the four condemned skills are Anthropic's
own first-party document skills. A gate wired to this output would block `docx`, `pptx` and `xlsx`
on a byte-order mark and a `rm` of the skill's own temp file.

The scoring compounds it: `docx` and `pptx` both hit exactly 100/100 with a `max_issue_severity` of
only HIGH. Volume of low-confidence matches, not the severity of any single one, is what produces
CRITICAL — so a skill with many bundled vendor files is structurally more likely to be condemned
than a small malicious one.

**Two things this run does not establish:**

1. **The LLM stage never ran.** Three analyzers (`semantic_developer_intent`, `semantic_quality_policy`,
   `semantic_security_discovery`) were skipped for want of an API key — and that is precisely the stage
   designed to triage what static matching over-flags. An attempt via `SKILLSPECTOR_PROVIDER=claude_cli`
   failed: the provider resolved an empty model name and all 5 LLM calls failed, with the tool
   correctly reporting *"LLM stage degraded … report reflects static analysis only"*. So this is a
   verdict on **half the product**, and the honest framing is: static-only output is triage input,
   not a gate.
2. **Coverage was not complete anywhere it mattered.** `docx` 78.7%, `pptx` 75.0%, `xlsx` 73.6%; and
   `playwright-recording`, `import-memory`, `session-start-hook` and `d3-viz` scanned at **0.0%
   coverage** while still being assigned scores up to 49/100. A score derived from nothing inspected
   is worse than no score. Also, a `--recursive` run over 56 skills aborted after 10 on an aggregate
   safety ceiling and silently listed the other 46 as `<omitted>` — scanning one skill at a time is
   the only way to get a complete picture.

Credit where due: the tool is honest about its own degradation. It said the LLM stage failed, it said
the recursive scan was incomplete, and it reports per-skill coverage percentages. Those are exactly
the disclosures a scanner needs to be safe to build on.

## 5. What this means for `mcp-vet`

This is the most useful thing in the run: a live, measurable example of the failure mode our own
auditor has to avoid.

1. **Precision is the product.** A scanner that flags `os.environ.copy()` as exfiltration and a BOM as
   prompt injection trains its users to ignore it. `mcp-vet`'s "evidence with file:line for every
   claim" is the right instinct; the missing half is a confidence model that will output *nothing*
   rather than a low-confidence guess.
2. **Never let volume drive severity.** Score by the strongest verified finding, not by the count of
   weak matches. Otherwise bundle size becomes the dominant signal.
3. **Coverage must gate the verdict.** If a skill scanned at 0% coverage, refuse to emit a score.
   `mcp-vet` should treat "I could not read this" as a distinct outcome from "I read it and it is fine".
4. **Distinguish a skill's declared purpose from covert behaviour.** The `task-observer`
   self-modification hit is the shape of a real check, applied without asking whether the manifest
   declares the behaviour. Declared-and-approved is a different category from hidden.
5. **The one gap nobody covers is still open.** Section 4.3 of the previous pass proposed
   tool-description injection and schema-drift detection for MCP servers. SkillSpector scans *skills*,
   not MCP tool metadata, and its own prompt-injection rule fires on byte-order marks. The niche
   `mcp-vet` was aimed at is still unoccupied.

## 6. Reproducing

```bash
uv tool install --python 3.12 git+https://github.com/NVIDIA/skillspector.git
for d in ~/.claude/skills/synced/*/*/; do
  skillspector scan "$d" --no-llm --format json --output "per/$(basename "$d").json"
done
```

Scan one skill at a time — `--recursive` stops early on an aggregate ceiling and omits the rest.
