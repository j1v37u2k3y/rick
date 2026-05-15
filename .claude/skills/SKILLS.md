# rick_mcp Skills Catalog

This directory contains project-local Claude Code skills that orchestrate `rick_mcp` MCP
tools into higher-level workflows. Skills are auto-discovered by Claude Code when launched
from this repo. Each skill lives in its own subdirectory with a `SKILL.md` file containing
YAML frontmatter (name + description for trigger matching) and a markdown body (the
playbook).

## Design philosophy

Skills are **generic and forkable** — they work for any user who clones rick_mcp. Personal
content (vault paths, operator identity, voice mantras) lives outside the codebase in
`~/.rick_mcp/` per the project's identity-loading pattern (`rick_mcp/identity.py`). Skills
orchestrate MCP tools and return content to chat; they do NOT write to the operator's
filesystem. State persistence happens inside the MCP server (`rick_kill_chain`,
`rick_notes`, `rick_tracker`) where it's already wired.

## The <!-- counts:skills -->9<!-- /counts:skills --> skills

### Engagement lifecycle

| Skill                   | Purpose                                                            | Trigger phrases                                         |
|-------------------------|--------------------------------------------------------------------|---------------------------------------------------------|
| `/engagement-kickoff`   | Stand up a new client engagement: SOW → ROE → onboarding → tracker | "kickoff", "new engagement", "spin up <client>"         |
| `/htb-day`              | CTF / HTB kickoff variant (no SOW, just kill-chain)                | "start <boxname>", "htb day", "ctf kickoff"             |
| `/kill-chain-walk`      | Phase-by-phase guided op with state tracking — the daily driver    | "advance the kill chain", "what's next on <engagement>" |
| `/debrief-then-publish` | Close-out: debrief + report scaffolds + timeline + export          | "close out <engagement>", "wrap the engagement"         |

### Content production

| Skill              | Purpose                                                         | Trigger phrases                         |
|--------------------|-----------------------------------------------------------------|-----------------------------------------|
| `/writeup-publish` | Engagement → sanitized public writeup (CTF / blog / bug bounty) | "writeup <engagement>", "publish <box>" |
| `/voice-check`     | Lint markdown for voice drift (sugar-coat, hedges, padding)     | "voice check this", "lint this writeup" |

### Operations support

| Skill               | Purpose                                                       | Trigger phrases                                         |
|---------------------|---------------------------------------------------------------|---------------------------------------------------------|
| `/arsenal-report`   | Target description → ordered tool plan by 7-phase methodology | "what should I run against X", "arsenal for <scenario>" |
| `/cheatsheet-build` | Vuln class / attack stage → one-page pocket reference         | "cheatsheet for <topic>", "one-pager on <vuln class>"   |

### Career

| Skill            | Purpose                                                     | Trigger phrases                                |
|------------------|-------------------------------------------------------------|------------------------------------------------|
| `/resume-tailor` | Job posting → fit assessment + cover letter + resume tweaks | "should I apply", "tailor my resume to <role>" |

> **Voice registers live in the MCP server, not in skills.** Use `rick_mode` to activate the
> operator's persona prompts (`be_rick`, `mentor`, `evaluate`, etc.) for character / register
> shifts. Skills are workflow primitives; voice is server-canonical. One source of truth,
> no drift between channels.

## How skills compose

Skills are designed to chain. Common workflows:

**Paid client engagement lifecycle:**

```
/engagement-kickoff → /kill-chain-walk → /debrief-then-publish
                                       └→ /writeup-publish (if public-facing)
```

**CTF lifecycle:**

```
/htb-day → /kill-chain-walk → /writeup-publish
```

**Pre-engagement planning:**

```
/arsenal-report (target → tool plan) → /engagement-kickoff or /htb-day
```

**Mid-op deep dives:**

```
/cheatsheet-build (vuln class → pocket ref)
```

**Voice register shifts (apply during any of the above):**

```
rick_mode(persona="be_rick")   — operator default
rick_mode(persona="mentor")    — teaching / cycle-breaking conversations
rick_mode(persona="evaluate")  — formal client-deliverable register
```

Server-side persona prompts handle voice; skills handle workflow. Chain a `rick_mode`
call inside any skill output when the register needs to shift.

**Career adjacent:**

```
/resume-tailor (job posting → application package)
```

**Pre-publish QA:**

```
<any draft> → /voice-check → polish → ship
```

## MCP tool coverage

The skills collectively orchestrate the following `rick_mcp` tool families:

- **Engagement management:** `rick_engagement_proposal`, `rick_roe`,
  `rick_client_onboarding`, `rick_tracker`, `rick_scoping`, `rick_debrief`
- **Kill chain + state:** `rick_kill_chain`, `rick_sitrep`, `rick_next_move`,
  `rick_attack_chain`, `rick_timeline`, `rick_export`, `rick_notes`
- **Recon / vuln assessment:** `rick_recon`, `rick_recon_handle`, `rick_vuln_assess`,
  `rick_cve`, `rick_threat_model`
- **Exploitation / payload methodology:** `rick_payload_guide`, `rick_cheatsheet`,
  `rick_pivot_plan`, `rick_cloud_attack_path`
- **Defensive / remediation:** `rick_hardening`, `rick_detection_rules`,
  `rick_rollback`
- **Reporting:** `rick_report_template`
- **Career / advisory:** `rick_compatibility_check`, `rick_cover_letter`,
  `rick_mentorship`, `rick_tool_recommend`, `rick_capabilities`
- **Public writeups:** `rick_writeups`
- **Operator voice:** `rick_mantra`, `rick_mode`

Plus the MCP resources: `profile://`, `resume://`, `doc://`.

## Operating discipline (applies to all skills)

These three rules apply across the skill suite:

1. **Verify the premise before designing the fix.** Symptom reports get a quick diagnostic
   check before structural work. Diagnose first, fix second.
2. **Plan-first cadence; `AskUserQuestion` at config decision points.** Non-trivial work
   gets a brief plan + explicit pickers at every flag / mode / scope / path decision.
   Each answered question reduces surface area, not expands it.
3. **Re-stage after pre-commit hook fixes; new commit, never amend.** Hook-modified files
   require a fresh commit. `git commit --amend` after a hook abort rewrites previous
   commits and destroys in-progress work.

## Extending the catalog

To add a new skill:

1. Create `<skill-name>/SKILL.md` with the standard frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: >
     <description — the description is what triggers the skill matching, so be specific
     about purpose, trigger phrases, and out-of-scope cases>
   ---
   ```
2. Body sections (recommended order):
    - Prerequisites (MCP tools / external deps)
    - Inputs required (with `AskUserQuestion` defaults)
    - Workflow (numbered steps with concrete tool calls)
    - Acceptance criteria
    - Failure modes
    - Voice rules (if applicable)
    - What this skill does NOT do
    - Related skills
3. Append a row to this catalog under the appropriate category.
4. Run `make check` if a project-level test or lint touches the skill content.

## Author / lineage

These skills emerged from the rick_mcp operator practice — daily engagement work, CTF
training, client deliverables, vault knowledge management. The patterns reflect 22+ years
of offensive-security craft applied to the MCP era: orchestration over re-implementation,
state in the server not the playbook, voice registers as composition primitives.

Same craft, different battlefield.
