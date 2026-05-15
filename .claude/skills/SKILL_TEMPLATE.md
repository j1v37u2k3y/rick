---
name: skill-template
description: >
  <One paragraph. State the purpose, the trigger phrases, and the out-of-scope cases.
  The description drives natural-language matching, so be specific. Mention adjacent
  skills the user might also be thinking of so the matcher routes correctly. Include
  the `/<skill-name>` form as one of the trigger phrases.>
---

# <Skill Name>

> <One-line elevator pitch. Builder-metaphor framing if natural — what this skill
> orchestrates, in one breath.>

---

## Prerequisites

The `rick_mcp` MCP server must be connected. This skill calls:

- `mcp__rick_mcp__<tool_name>` — <one-line purpose>
- `mcp__rick_mcp__<tool_name>` — <one-line purpose>

<Skills are workflow primitives — they orchestrate MCP tools. If a skill has no MCP
tool dependencies, reconsider whether it should be a skill or a server-side persona
prompt in `rick_mcp/prompts.py`. Voice / register instructions belong server-side.>

---

## Inputs required

If the operator hasn't supplied these, **ask via `AskUserQuestion` before firing any
tool** (plan-first cadence; ask at config decision points):

1. **`<input_name>`** — <type, constraints, default if any>.
2. **`<input_name>`** *(optional)* — <type, constraints, default>.

---

## <Skill-specific section> *(optional)*

<Use this slot for vocabulary mappings, decision matrices, or any reference table
the workflow depends on. `engagement-kickoff` uses it for the proposal-vs-ROE
vocabulary mapping. Delete this section if not needed.>

---

## Workflow

Run sequentially unless otherwise noted.

### Step 1 — <Step name>

```
mcp__rick_mcp__<tool>({
  params: {
    <param>: "<value>",
    response_format: "markdown"
  }
})
```

<What this step accomplishes. Capture any returned handles the later steps need.>

### Step 2 — <Step name>

<Continue numbered steps. Each step gets a concrete tool call block where
applicable.>

### Step N — Output

<Define the response structure: section order, what gets included verbatim, what
gets summarized. Operators copy-paste skill output into other systems — make the
shape predictable.>

---

## Acceptance criteria

- [ ] <Concrete check — "all tool calls returned successfully, no truncation">
- [ ] <Concrete check — "<handle> captured and returned to the operator">
- [ ] <Concrete check — "summary shows the next concrete move">

---

## Failure modes

- **<Failure scenario>** — <how to surface the error and recover. Default: surface,
  ask whether to retry or roll back.>
- **<Failure scenario>** — <handling>

---

## Voice

<Operational by default. Honest scope, no padded estimates. Voice / register shifts live
in the MCP server's persona prompts (`rick_mcp/prompts.py`), not in skills. If the skill
output needs a register shift, recommend `rick_mode(persona="be_rick" | "mentor" |
"evaluate" | ...)` rather than encoding voice instructions in the skill itself. One source
of truth for voice — server-canonical.>

---

## What this skill does NOT do

- <Out-of-scope item — name the adjacent skill that handles it>
- <Out-of-scope item — name the adjacent skill that handles it>

---

## Related skills

- `/<adjacent-skill>` — <relationship — when to use this one instead>
- `/<adjacent-skill>` — <relationship>
