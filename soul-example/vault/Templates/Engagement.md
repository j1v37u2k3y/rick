---
type: template
ai-first: true
template-target: engagement
---

## For future Claude

Engagement note template — what `rick_engagement_proposal` writes (in proposal-shape).
Forkers can adapt this template. The structure below is what the rick_mcp engagement tools
expect to find / append to.

# {{Client}} — {{Engagement Type}}

> **Status:** scoping
> **Prepared by:** [[Identity/Operator]]
> **Date:** {{YYYY-MM-DD}}
> **Recommended duration:** {{N}} business days
> **Requested duration:** {{N}} business days

## Summary

<One-paragraph engagement overview — what's in scope, what's not, what the deliverable
is.>

## Scope

- <In-scope target>
- <In-scope target>

**Out of scope:** <explicit exclusions>

## Methodology

Follows the operator's 7-phase methodology — see [[Identity/Methodology]].

1. Reconnaissance
2. Vulnerability Assessment
3. Exploitation
4. Privilege Escalation
5. Lateral Movement
6. Documentation
7. Remediation Strategy

## Specialization wikilinks

- [[Identity/Specializations/<spec>]] *(populated by `rick_engagement_proposal`)*

## Tool wikilinks

- [[Identity/Tools/<tool>]] *(populated by `rick_engagement_proposal`)*

## Deliverables

- Executive summary
- Technical findings (PlexTrac-compatible structure)
- Remediation guidance per finding
- Optional: presentation / debrief

---

*This template is what `rick_engagement_proposal` produces. ROE, onboarding, and debrief
sections append to the same file when those tools are invoked for this engagement.*
