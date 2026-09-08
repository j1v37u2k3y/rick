# Why Rick?

*Read this if you're standing in front of the fork button wondering whether it's worth it.*

You like the voice. Good. That's the hook — it is **not** the reason. Nobody forks a tool because it talks
pretty. So let me hand you the load-bearing walls first, and we'll get to the voice when it's earned its place.

## The one-liner

**rick_mcp is a forkable MCP server that gives Claude a memory of your op and a copy of your methodology —
then serves both back on demand, in a voice you actually want in the trench with you.**

Fork it. Overlay your identity. Get to work.

## The problem it fixes

Claude is sharp. Claude is also a goldfish. Every session you open, you re-introduce yourself — who you are,
how you work, what phase the engagement is in, what you already found. *You're* the one holding the state in
your head, and your head is busy enough with the target.

Generic assistant, generic answers, zero continuity. That's the crack in the foundation. Rick patches it.

## What you actually get

Not a prompt pack. A platform. **48 tools, 36 resources**, wired to a real 7-phase methodology
(PTES + OWASP + MITRE ATT&CK):

- **Memory that survives the session.** Kill chain, findings, timeline, sitrep — persisted to disk, not to the
  chat window. Close the laptop, come back tomorrow, run `rick_sitrep`, and you're standing exactly where you
  left off. Rick holds the op so you don't have to.
- **Your methodology, encoded.** Recon → vuln assess → exploit → escalate → pivot → document → remediate. Not
  notes in a wiki you never open — callable tools that emit the playbook the same way every time.
- **The whole engagement lifecycle.** Scoping → ROE → onboarding → tracker → debrief → report → sanitized
  public writeup. The business end of the work, standardized, so your hours go to the target instead of the
  paperwork.
- **Forkable skills.** Claude Code skills that orchestrate the tools — kick off an engagement, walk a kill
  chain phase by phase, close it out. They ride along with the fork.
- **The server IS the resume.** Profile, methodology, and evidence are queryable resources. Every tool proves a
  claim. Point a recruiter's AI at it, or point your own at it mid-op — same surface, no drift.

## Why *you* can fork it without leaking a byte

Here's the design decision that makes this yours and not mine:

**Public template, private overlay.** The repo ships generic. Every scrap of identity — profile, soul, vault,
writeups — loads from `~/.rick_mcp/` at runtime, and that directory never touches git. You fork the machine.
You drop in your own `identity.yaml`. It becomes *you* — your name on the work, none of mine in your commits.

That's not luck. That's a load-bearing wall, poured on purpose.

## Built like my name's on it

Because it is. This isn't a weekend hack you're inheriting:

- Typed end to end (Pydantic v2), tested hard, coverage floored — not aspirational, enforced.
- File-length limits, pre-commit gates, and licensing hygiene so a public, network-served fork doesn't trip
  somebody else's copyleft.
- Measure twice, cut once. Foundation-first — a bad joint brings down everything sitting on top of it.

Fork it as a reference for how to build an MCP server *right*, even if you strip every tool out and start over.

## And yeah — the voice

Last, because it earns its place last. The persona layer gives you a voiced operator — honest, no
sugar-coating, no checkbox compliance, **do no harm** carved into the soul as the first principle —
non-negotiable, everything else bolts onto it. The reference fork's voice is Rick: the father, the builder
bloodline, slow-is-smooth-smooth-is-fast. Yours is whatever you build in its place.

You'll stay for the substance. You'll *enjoy* it because of the voice. That's the right order — get it
backwards and you've got a toy.

## Make it yours in 60 seconds

```bash
git clone <your-fork>
cd rick && make setup          # deps, hooks, ~/.rick_mcp/ scaffold
# drop your identity.yaml + soul/ into ~/.rick_mcp/
```

Then `be_rick` — or be whoever you are. The machine's the same. The bloodline's yours now.

*I'm still building. Are you?*
