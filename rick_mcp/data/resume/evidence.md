# Skill-to-Tool Evidence Map

## Exhibits

### rick_recon

**Demonstrates:** Offensive security methodology, OSINT tradecraft, multi-platform recon (8 target types), tool
selection expertise
**Try it:** `rick_recon(target_type='active_directory')` — see the BloodHound-first methodology and ADCS focus that
comes from real AD engagements.

### rick_vuln_assess

**Demonstrates:** OWASP expertise, vulnerability classification depth, testing technique knowledge (10 categories),
risk-based severity understanding
**Try it:** `rick_vuln_assess(vuln_category='idor')` — BOLA/IDOR methodology that reflects hands-on API testing
experience.

### rick_roe

**Demonstrates:** Engagement management, legal/authorization awareness, client communication, escalation protocol design
**Try it:** `rick_roe(engagement_type='red_team', client_name='Your Company', duration_days=20)`

### rick_report_template

**Demonstrates:** Professional documentation, PlexTrac workflow, executive communication, evidence chain of custody
**Try it:** `rick_report_template(section='finding', finding_title='SQL Injection in Auth', severity='critical')`

### rick_tool_recommend

**Demonstrates:** Tool ecosystem knowledge, scenario analysis, practical experience with 30+ security tools
**Try it:** `rick_tool_recommend(scenario='internal network pentest with Active Directory and cloud Azure environment')`

### rick_engagement_proposal

**Demonstrates:** Business development, SOW/proposal writing, scope estimation, timeline planning
**Try it:** `rick_engagement_proposal(engagement_type='full_scope', client_name='Enterprise Corp', estimated_days=25)`

### rick_client_onboarding

**Demonstrates:** Client management, process design, communication protocols, operational planning
**Try it:** `rick_client_onboarding(client_name='New Client Inc')`

### rick_compatibility_check

**Demonstrates:** Self-awareness, honest fit assessment, keyword analysis, professional judgment
**Try it:** Paste your actual job posting or engagement brief and see the analysis.

### rick_cover_letter

**Demonstrates:** Written communication, audience adaptation (3 tones), requirement matching, professional presentation
**Try it:**
`rick_cover_letter(company_name='Your Company', role_title='Senior Pentester', key_requirements='OSCP web app cloud leadership')`

---

## The Server Itself Demonstrates

- Python/FastMCP/Pydantic v2 fluency — the code IS the code sample
- MCP protocol design — proper tool vs resource separation
- Architecture judgment — lean by design, no redundancy
- Security-first thinking — input validation, ConfigDict(extra='forbid'), type safety
- Craftsmanship — builder heritage visible in code quality
- Builder mindset — this is a product, not a script