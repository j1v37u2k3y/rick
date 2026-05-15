---
name: resume-tailor
description: >
  Given a job posting (text paste or URL), produce a fit assessment + tailored cover letter +
  recommended resume tweaks aligned to the role. Orchestrates rick_compatibility_check,
  rick_cover_letter, and the resume:// MCP resource family. Use this skill when the operator
  shares a job posting and wants the application package tailored, asks "should I apply",
  "is this a fit", "draft a cover letter for X", "tailor my resume to <role>", or invokes
  "/resume-tailor". The output is a draft package, not a submission — the operator reviews
  and decides.
---

# Resume Tailor

> Match the evidence to the role like mortar to brick — every line earns its place. Honest
> fit, sharp draft.

---

## Prerequisites

`rick_mcp` MCP server connected. This skill calls:

- `mcp__rick_mcp__rick_compatibility_check` — fit assessment (tech + cultural alignment)
- `mcp__rick_mcp__rick_cover_letter` — tailored letter, 3 tone options
- `ReadMcpResourceTool` — for `resume://overview`, `resume://evidence`, `resume://portfolio`,
  `resume://contact`
- `WebFetch` — if the operator supplied a URL instead of pasted text

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **Job posting source** — paste text (10–3000 chars) OR URL.
2. **Company name** — extracted from posting if obvious; ask if ambiguous. Max 100 chars.
3. **Role title** — same handling. Max 200 chars.
4. **Tone** — `professional` (default), `conversational`, or `executive`. Pick based on the
   role (defense contractor → professional; startup → conversational; CISO track → executive).

---

## Workflow

### Step 1 — Acquire the posting text

If URL provided:

```
WebFetch({ url: "<url>", prompt: "Extract the full job posting text including responsibilities, requirements, qualifications, and any tech stack mentions. Return verbatim." })
```

If text pasted, validate it's 10–3000 chars. If > 3000, ask whether to truncate boilerplate
or pick the most-relevant 3000.

### Step 2 — Compatibility check

```
mcp__rick_mcp__rick_compatibility_check({
  params: {
    description: "<posting text>",
    eval_type: "role",
    response_format: "markdown"
  }
})
```

### Step 3 — Pull resume context

In parallel:

```
ReadMcpResourceTool({ server: "rick_mcp", uri: "resume://overview" })
ReadMcpResourceTool({ server: "rick_mcp", uri: "resume://evidence" })
```

Pull `resume://portfolio` only if the posting emphasizes public work / GitHub / blog.
Pull `resume://contact` only if the posting requires specific outreach format.

### Step 4 — Extract key requirements

Skim the posting. List 4–8 concrete requirements / responsibilities to address in the cover
letter. Examples: "5+ years offensive security," "OSCP or equivalent," "experience leading
red team engagements," "Python automation."

### Step 5 — Generate cover letter

```
mcp__rick_mcp__rick_cover_letter({
  params: {
    company_name: "<from input>",
    role_title: "<from input>",
    key_requirements: "<comma-joined list, ≤1000 chars>",
    tone: "<from input>",
    response_format: "markdown"
  }
})
```

### Step 6 — Draft resume tweaks

Cross-reference posting requirements against `resume://evidence`. Surface 3–6 specific edits
to sharpen the resume for this role:

- **Reorder evidence** — push role-relevant items to the top.
- **Reweight specializations** — emphasize the 2–3 that match.
- **Add/expand bullets** — reference specific war stories, engagements, or projects that
  prove the requirements (pull from `doc://war_stories` if relevant).
- **Trim** — call out which items are dead weight for this role.

Be specific. Don't say "add cloud experience" — say "add 1 bullet under offensive security
referencing the AWS engagement" with exact wording.

### Step 7 — Output

Single markdown report. Sections in order:

1. **Role** — Company, Title, source (URL or pasted)
2. **Fit Assessment** — from Step 2
3. **Key Requirements Identified** — from Step 4
4. **Cover Letter Draft** — from Step 5
5. **Resume Tweaks** — from Step 6
6. **Recommended Next Action** — one line: apply / pass / dig deeper / negotiate intro

---

## Acceptance criteria

- [ ] Fit assessment in the output (not skipped even if posting looks great)
- [ ] Cover letter is ≤ 1 page when rendered
- [ ] Resume tweaks are specific (exact bullets, exact reorderings — not "add more cloud")
- [ ] Tone matches the role context
- [ ] Recommended next action is a single concrete verb, not a paragraph

---

## Failure modes

- **`rick_compatibility_check` returns low fit (< 50%)** — surface honestly. Don't pad the
  cover letter to compensate. Honest fit is the point.
- **Posting is too short to extract requirements** — ask operator for context (full link,
  description).
- **WebFetch fails on URL** — ask operator to paste the text.
- **Resume evidence doesn't match the role** — say so. Recommend `pass` or `dig_deeper`
  instead of forcing a cover letter that misrepresents.

---

## Voice

Career-facing material. Honest fit, no padding. The configured operator persona (see
identity loader) sets the substance; tone parameter sets the audience-facing register.
Three tones map to three contexts — pick the one that respects the audience.

---

## What this skill does NOT do

- Submit the application — the operator reviews and submits.
- Negotiate salary or terms — separate conversation.
- Update the canonical resume files — those edits are the operator's call after review.

---

## Related skills

- `/be_rick` — invoke the operator persona for character if desired
- `/engagement-kickoff` — if the role is a contract / consulting opportunity, kickoff after acceptance
