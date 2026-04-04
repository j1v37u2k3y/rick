# Soul Example — Make Rick Yours

This directory contains fully worked examples for configuring your Rick MCP identity, using a fictional operator *
*sh4d0wf0x** (Alex Chen). Copy the files to `~/.rick_mcp/` and replace the content with your own.

## Quick Setup

```bash
# Copy the example files (excluding this README)
cp soul-example/identity.yaml ~/.rick_mcp/
cp -r soul-example/soul soul-example/profiles soul-example/resume soul-example/docs ~/.rick_mcp/

# Edit identity.yaml with your details
$EDITOR ~/.rick_mcp/identity.yaml
```

## File Structure

```
~/.rick_mcp/
    identity.yaml          # Core identity config (callsign, certs, tools, etc.)
    soul/
        SOUL.md            # Your core principles and values
        my book.txt        # Your memoirs, your story, your voice
        PROFILE.md         # Current state, what's on the horizon
    profiles/
        summary.md         # Quick reference card
        values.md          # Core values
        heritage.md        # Your background and roots
        craftsmanship.md   # Your philosophy of craft
        stack.md           # Technical arsenal
        methodology.md     # Engagement methodology
        mantras.md         # Operational mantras
        human.md           # The human element
        entertainment.md   # Humor and morale
        timeline.md        # Career timeline
    resume/
        overview.md        # Resume overview
        evidence.md        # Skill-to-tool mapping
        portfolio.md       # Portfolio links
        contact.md         # Contact information
    docs/
        war_stories.md     # Anonymized engagement narratives
```

## How It Works

1. **identity.yaml** is the core config. Rick loads this at startup and uses it everywhere — tool output, prompts,
   status, signatures. Without it, Rick runs with generic defaults.

2. **soul/** files feed the MCP prompts. When you activate `be_rick` mode, the soul and book content get injected live.
   Update the soul, update Rick's voice.

3. **profiles/** and **resume/** serve as MCP resources. Any MCP client can query `profile://summary` or
   `resume://overview` and get your identity data back.

4. **docs/** contains additional content like engagement war stories.

## What Happens Without Identity

Rick works fine without any of these files. Tools fire, tests pass, everything is operational. You just get generic
output instead of personalized content. The security methodology is in the code — the identity is in the config.

## Tips

- Start with just `identity.yaml` — that alone personalizes most output
- Add `soul/SOUL.md` next — it powers the `be_rick` prompt mode
- Profile and resume files are for the living resume feature
- War stories should be anonymized — no client names, no specifics that could identify an engagement
