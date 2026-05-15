---
name: voice-check
description: >
  Lint markdown content for voice drift against the operator's configured tone. Catches
  sugar-coating, padded hedges, checkbox-compliance phrasing, weasel words, false-precision
  numbers, and over-sanitized passive voice — common drift patterns when AI-generated or
  collaborative prose gets reviewed for an offensive-security context. Use this skill when
  the operator wants to lint a writeup, report draft, blog post, or any markdown content
  before shipping: "voice check this", "lint this writeup", "review tone of <file>",
  "/voice-check". Returns a structured findings list grouped by severity, with proposed
  rewrites for each finding. Not for grammar correction (use a real linter) or fact-checking
  (use a research tool or vault history).
---

# Voice Check

> Sugar-coat doesn't ship. Hedge words don't earn trust. Sanitized passive voice drains
> authority from technical content. This skill catches the drift before publication.

---

## Prerequisites

No MCP tools required. This is a pure-prose linter that runs against markdown content
supplied by the operator (file path or pasted text).

Optional: `mcp__rick_mcp__rick_mantra` to pull operator-configured voice mantras for
context. `mcp__rick_mcp__rick_mode` to check what persona register is currently active.

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **Source** — absolute file path to a markdown file OR pasted text.
2. **Target tone** *(optional)*:
   - `operational` (default) — terse, first-person, no hedging, USMC-style
   - `formal` — client report register, third-person allowed, hedged when uncertain
   - `mentor` — teaching voice, patient, second-person, scaffolded explanations
   - `executive` — board-room register, abstracted, business-impact framing
3. **Strictness** *(optional)*:
   - `advisory` (default) — surface findings, suggest rewrites
   - `strict` — flag every drift pattern, even minor ones
   - `lenient` — only flag major drift

---

## Voice drift patterns (the linter rules)

### 🔴 Critical drift — flagged at all strictness levels

| Pattern               | Example                                              | Why it drifts                         |
|-----------------------|------------------------------------------------------|---------------------------------------|
| Sugar-coat            | "We discovered a minor issue worth considering."    | Hides severity; erodes trust.        |
| Checkbox compliance   | "Best practices were followed throughout."           | Says nothing; padding.               |
| Hedging-as-cover      | "It might possibly perhaps suggest that..."          | Triple-hedge = no claim made.        |
| False precision       | "We tested 73.2% of the attack surface."             | Made-up specificity; lose credibility.|
| Marketing voice       | "Cutting-edge AI-powered solutions..."               | Hollow buzzwords; non-technical.     |
| Generic platitudes    | "Security is a journey, not a destination."          | Says nothing; padding.               |

### 🟡 Moderate drift — flagged in `advisory` and `strict`

| Pattern               | Example                                              | Fix direction                         |
|-----------------------|------------------------------------------------------|---------------------------------------|
| Passive over-use      | "The vulnerability was identified by the team."      | Active: "We found <vuln>."            |
| Adjective stacking    | "A critical severe high-impact vulnerability..."     | Pick one severity word.               |
| Weasel words          | "Some experts say..."                                | Cite or drop.                         |
| Filler intros         | "It is important to note that..."                    | Cut; start with the noun.             |
| Verbose connectives   | "In order to be able to perhaps..."                  | Cut to "to".                          |

### 🟢 Minor drift — flagged only in `strict`

| Pattern               | Example                                              | Fix direction                         |
|-----------------------|------------------------------------------------------|---------------------------------------|
| Vague time refs       | "Recently observed activity..."                      | Specific date.                        |
| Number→word inconsistency | "We had 5 findings and three were critical."     | Pick one form.                        |
| Sentence-start "And/But/So" | (acceptable in operational; flagged in formal)| Tone-conditional.                     |
| Trailing emoji        | "We rooted it. 🎉"                                   | Tone-conditional.                     |

---

## Tone-specific overrides

| Target tone | Adjustments                                                            |
|-------------|------------------------------------------------------------------------|
| operational | First-person required. Passive voice = 🔴. "And/But" sentence starts OK.|
| formal      | Third-person preferred. Hedged uncertainty OK. Emoji = 🔴.             |
| mentor      | Second-person OK. Patience + scaffolding > terseness.                  |
| executive   | Business-impact framing required. Technical detail = 🟡 (route to appendix). |

---

## Workflow

### Step 1 — Acquire source

If file path: `Read` the file.
If pasted text: use as-is.

Validate it's markdown content (not binary, not empty).

### Step 2 — Optional: load operator voice context

```
mcp__rick_mcp__rick_mantra({ params: { response_format: "markdown" } })
mcp__rick_mcp__rick_mode({ params: {} })
```

Use these to calibrate — if the operator's configured persona has explicit voice rules,
honor them over the defaults.

### Step 3 — Walk the content

Scan section by section. For each drift pattern from the rule tables, flag:

- **Location** — line number or section header
- **Pattern matched** — name from the table
- **Severity** — 🔴 / 🟡 / 🟢
- **Excerpt** — the offending phrase (max 100 chars)
- **Proposed rewrite** — concrete replacement, tone-appropriate

Apply tone-specific overrides from the previous table.

### Step 4 — Aggregate findings

Group by severity. Within each severity, order by line number.

### Step 5 — Output

Single markdown report. Structure:

```markdown
# Voice Check — <source identifier>

**Target tone:** <picked>
**Strictness:** <picked>
**Total findings:** <N>

## 🔴 Critical (<count>)

### Finding 1 — <pattern name>
- **Location:** line <N> (`## Section Header`)
- **Excerpt:** "<offending phrase>"
- **Rewrite:** "<proposed replacement>"
- **Why:** <one-line rationale>

(...)

## 🟡 Moderate (<count>)
(...)

## 🟢 Minor (<count>)
(...)

## Summary
- Critical: <count>
- Moderate: <count>
- Minor: <count>
- **Recommendation:** ship as-is / one polish pass / major rewrite needed
```

### Step 6 — Optional: auto-apply rewrites

If the operator confirms via `AskUserQuestion` after Step 5, apply the proposed rewrites
via `Edit` to the source file. Surface each replacement as a single Edit call. Operator
sees each before approving.

If text was pasted (not a file), skip auto-apply — return the rewritten text alongside the
findings instead.

---

## Acceptance criteria

- [ ] Every flagged pattern has a concrete proposed rewrite (not "consider revising")
- [ ] Findings ordered by severity then line number
- [ ] Tone-specific overrides applied correctly
- [ ] Summary recommendation is one of: ship / polish / rewrite
- [ ] No findings flagged as 🔴 for patterns that fit the target tone (e.g. passive voice
      in `formal` tone)

---

## Failure modes

- **Source empty / not markdown** — surface to operator; ask for valid input.
- **No findings detected** — return "✅ Voice clean for target tone <X>" + a short note on
  why (e.g. "Active voice throughout, no hedge clusters, no padding").
- **Conflicting tone signals in the content** — e.g. half operational, half formal. Surface
  the conflict; ask operator which tone the section should belong to.
- **Auto-apply would change tone-load-bearing phrasing** — pause; surface to operator.

---

## Voice

The linter itself follows operational voice — terse, direct, every finding earns its line.
No padding the report.

---

## What this skill does NOT do

- Grammar / spelling correction — use a real linter (markdownlint, vale).
- Fact-checking — use a research tool or vault history.
- Translate between tones — flags drift FROM the target tone, doesn't convert between tones.
- Censorship — flags drift from authenticity, not from politeness.

---

## Related skills

- `/writeup-publish` — run voice-check before publishing
- `/debrief-then-publish` — run voice-check on report scaffolds before client delivery
9- `rick_mode(persona="evaluate")` — pair with this skill for formal-register passes (server-side persona)
- `rick_mode(persona="be_rick")` — restore character voice if a draft drifted into corporate-sterile
