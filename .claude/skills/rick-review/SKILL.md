---
name: rick-review
description: >
  Point Rick at a codebase and get his honest, builder's-eye verdict — craftsmanship, security,
  and architecture — in his own voice. Hybrid orchestrator: if there's a diff or open PR, it
  delegates the heavy analysis to Claude Code's built-in code-review (bugs + reuse / simplification /
  efficiency) and security-review (security of pending changes), then re-prioritizes and re-voices
  the findings through Rick's rubric; if it's a cold repo with no changes, Rick walks the
  load-bearing files himself via the rick_code_review rubric. Use this skill when the operator wants
  Rick's take on a codebase: "scan this codebase", "rick's honest opinion on this repo", "what does
  rick think of <path>", "review this code like rick", "/rick-review". It wraps and adds a verdict
  layer on top of the built-in code-review and security-review engines — it does NOT replace them,
  and it is not `/voice-check` (prose linting) or the simplify cleanup pass.
---

# Rick Review

> Point me at the codebase and I'll tell you the truth about it — not what you want to hear. Where
> the load-bearing walls are, where the joints leak, what ships and what needs the foundation
> redone. No padded reports. Every crack comes with a blueprint to fix it.

---

## Prerequisites

- **`rick_code_review`** (MCP) — the builder's-eye scoring & verdict rubric. The lens everything
  gets scored against.
- **Built-in `code-review` skill** — diff-scoped correctness + reuse / simplification / efficiency.
  Invoke it via the Skill tool (e.g. `Skill(skill="code-review")`). Effort levels low → max → ultra;
  `ultra` runs in the cloud and is billed — **never auto-run it; recommend and let the operator
  trigger.**
- **Built-in `security-review` skill** — security review of pending changes. Invoke via the Skill
  tool (`Skill(skill="security-review")`).
- **`mcp__rick_mcp__rick_vuln_assess`** / **`mcp__rick_mcp__rick_threat_model`** — security
  methodology depth when a vuln class or trust boundary is implicated.
- **`mcp__rick_mcp__rick_mode`** — pull Rick's persona register for the final verdict voice.
- Native `git` / Glob / Read — for mode detection and the cold-repo scan.

This skill is **pure orchestration**: it reads the tree and composes tools. It does not write to the
operator's filesystem and stays advisory (it may *recommend* the operator run a fix pass, never
auto-applies one).

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **Scope** — path to the repo/dir (default: current working directory), or a PR number.
2. **Lens** *(optional)* — `full` (default, craftsmanship + security + architecture), `security`,
   `craftsmanship`, or `architecture`. Maps to the tool's `focus`.
3. **Effort** *(optional)* — for the built-in code-review engine in diff mode: `low` / `medium`
   (default) / `high` / `max`. **`ultra` is billed/cloud — surface it as an option the operator must
   explicitly choose; never default to it.**
4. **Strictness** *(optional)* — `advisory` (default, surface + recommend), `strict` (flag every
   drift), `lenient` (blockers only).

---

## Modes

| Trigger condition | Mode | How findings are gathered |
|-------------------|------|----------------------------|
| Uncommitted changes / a branch diff / a passed PR# | **diff mode** | Delegate to the built-in code-review + security-review engines, then score their output. |
| Clean repo, no diff | **cold mode** | Rick walks the load-bearing files himself using the rubric's `inspection_method`; security depth from `rick_vuln_assess`. |

Detect the mode in Step 2 — don't ask the operator to know it.

---

## Workflow

### Step 1 — Confirm scope, lens, effort

Resolve the four inputs above via `AskUserQuestion`. Default scope to cwd, lens to `full`.

### Step 2 — Detect the mode

```
git status --porcelain && git diff --stat HEAD
```

Changes present (or a PR# was given) → **diff mode**. Clean tree → **cold mode**.

### Step 3 — Pull the verdict rubric

```
mcp__rick_mcp__rick_code_review({
  params: { focus: "<lens>", language: "<primary repo language or omit>", response_format: "markdown" }
})
```

This is the scoring scale, the verdict scale, the dimension checklists, and the `inspection_method`.
Everything downstream gets normalized against it.

### Step 4 — Gather findings

**Diff mode** — delegate; don't reinvent:

```
Skill(skill="code-review", args="<effort> <path-or-PR>")          # bugs + reuse/simplification/efficiency
Skill(skill="security-review")                                    # security of pending changes (if lens includes security)
```

Collect their findings verbatim. For any security finding that implicates a known vuln class, deepen
with:

```
mcp__rick_mcp__rick_vuln_assess({ params: { vuln_category: "<class>", response_format: "markdown" } })
```

**Cold mode** — Rick scans:

- Glob the tree; identify the load-bearing modules, the biggest files, and whether tests exist.
- Read representative load-bearing files; apply the rubric's three dimensions.
- The built-in security-review has limited reach with no diff, so lean on
  `mcp__rick_mcp__rick_vuln_assess` (and `mcp__rick_mcp__rick_threat_model` for attack surface)
  against the smells you find.

### Step 5 — Normalize + prioritize

Map every finding — yours, code-review's, security-review's, vuln_assess's — onto the rubric's
severity scale (🔴 / 🟡 / 🟢). One finding, one severity. **Load-bearing first**: a 🔴 in a module
everything depends on outranks ten 🟢s in a leaf.

### Step 6 — Voice

```
mcp__rick_mcp__rick_mode({ params: { mode: "be_rick" } })
```

Render the verdict in Rick's register — builder metaphors, USMC-grade honesty, dry humor. Voice is
server-canonical; do not hand-author a tone here.

### Step 7 — Output

Single markdown report:

```markdown
# Rick Review — <repo/path/PR>

**Mode:** diff | cold   **Lens:** <lens>   **Verdict:** <one of the verdict scale>

## 🔴 Critical (<count>)
### <finding title>
- **Location:** <file:line / module>
- **Impact:** <what breaks / what's exposed — blast radius>
- **Blueprint:** <the concrete fix>
- **Source:** rick | code-review | security-review | vuln_assess

## 🟡 Moderate (<count>)
...

## 🟢 Minor (<count>)
...

## The Verdict
<Rick's voiced bottom line + the one verdict-scale call>
```

Then — advisory only — recommend next steps the operator can run themselves (e.g. the built-in
code-review with `--fix` or `--comment`, or a higher effort/`ultra` pass). Never auto-apply.

---

## Acceptance criteria

- [ ] Mode detected automatically (diff vs cold), not asked of the operator.
- [ ] Diff mode delegates to the built-in code-review (+ security-review when the lens includes
      security) instead of re-implementing analysis.
- [ ] Every finding carries location · impact · blueprint-to-fix · source.
- [ ] Findings grouped by severity, ordered load-bearing-first.
- [ ] Exactly one overall verdict from the rubric's verdict scale.
- [ ] Verdict rendered in `be_rick` voice via `rick_mode` — not hand-authored tone.
- [ ] `ultra` never auto-run; recommended only.
- [ ] No filesystem writes; output is chat-only and advisory.

---

## Failure modes

- **Not a git repo** — cold mode only; say so, scan the path directly, note that diff-engine
  delegation is unavailable.
- **Empty diff but operator expected changes** — surface it; confirm the branch/working tree before
  falling back to cold mode.
- **Built-in engine returns nothing** — report it honestly ("code-review found no issues in the
  diff") rather than padding the verdict to look thorough.
- **Huge repo** — in cold mode, scope to the load-bearing modules and **say what you skipped**.
  Silent truncation reads as "I reviewed everything" when you didn't.
- **Security lens on a cold repo** — flag the reduced reach; lean on `rick_vuln_assess` and
  recommend a branch-scoped `security-review` once there are changes.

---

## Voice

The report is operational and honest by default; the final verdict shifts to Rick's character via
`rick_mode(persona="be_rick")`. Voice / register is server-canonical (`rick_mcp/prompts.py`) — this
skill composes it, never duplicates it.

---

## What this skill does NOT do

- **Replace the built-in engines.** It wraps `code-review` and `security-review` and adds the
  builder's-eye verdict + voice. For a raw diff review, use them directly.
- **Auto-fix or auto-comment.** Advisory only — it recommends, the operator triggers.
- **Run billed `ultra` on its own.** Operator-triggered.
- **Write to the filesystem.** Findings go to chat.
- **Lint prose.** That's `/voice-check`.

---

## Related skills

- `/cheatsheet-build` — turn a recurring vuln class from the review into a pocket reference.
- `/arsenal-report` — if the review pivots into an actual engagement against the target.
- `/voice-check` — lint the report's prose before it ships to a client.
- `rick_mode(persona="be_rick")` — the voice register the verdict is rendered in (server-side persona).
- `rick_mode(persona="evaluate")` — formal register if the verdict goes into a client deliverable.
