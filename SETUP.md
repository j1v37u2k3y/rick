# Setup — From Clone to Running Rick

Linear walkthrough. Clone the repo, follow the steps in order, end with a working Rick MCP server
accessible from Claude Code. Each step has a **Verify** line — if it doesn't return what's described,
jump to [Troubleshooting](#troubleshooting) before continuing.

Optional layers (identity, Kali VM, Docker, Claude Desktop) come after the core path. Skip what doesn't
apply to you.

---

## Prerequisites

| Required     | Why                                                      |
|--------------|----------------------------------------------------------|
| Python 3.10+ | The server runs on FastMCP, which requires 3.10 or newer |
| `git`        | Cloning the repo                                         |
| `make`       | Run the bundled setup + check pipelines                  |

| Optional             | Why                                                                               |
|----------------------|-----------------------------------------------------------------------------------|
| Claude Code CLI      | Easiest way to talk to Rick — auto-discovers `.mcp.json`                          |
| Claude Desktop       | Alternative client (see [Claude Desktop](#optional--claude-desktop))              |
| VMware Fusion + Kali | If you want to run engagements from Kali while Obsidian indexes notes on the host |
| Docker               | Containerized run (see [Docker](#optional--docker))                               |

Check your Python version:

```bash
python3 --version    # need 3.10+
```

If you see 3.9 or older, install a newer Python (Homebrew on macOS: `brew install python@3.12`).

---

## Core path

Four steps. End state: `rick_capabilities` returns a full tool map inside Claude Code.

### Step 1 — Clone + setup

```bash
git clone https://github.com/j1v37u2k3y/rick.git
cd rick
make setup
```

`make setup` does four things:

1. Creates a local venv at `./venv/` if it doesn't already exist
2. Installs Python deps into that venv via `venv/bin/pip`
3. Installs pre-commit hooks (so commits get auto-linted)
4. Creates `~/.rick_mcp/` — the private content directory on your host

**Verify:**

```bash
test -d venv && echo "venv: OK"
test -d ~/.rick_mcp && echo "private dir: OK"
ls .git/hooks/pre-commit && echo "hooks: OK"
```

All three should print `OK`. If any fails, see [`make setup` fails](#make-setup-fails).

### Step 2 — Sanity-check the install

```bash
make test
```

**Verify:** the test suite passes. Latest baseline shown in the README badge (currently 794 tests).

You do **not** need to `source venv/bin/activate` first — every `make` target uses `venv/bin/<tool>`
directly, so they all work the moment `make setup` finishes. (Activate the venv only if you want to
run `python` / `pip` / `pytest` directly in your shell for ad-hoc work.)

If tests fail right after a clean clone, that's a real bug — open an issue with the failure output.

### Step 3 — Open with Claude Code

The repo ships `.mcp.json` at the root. Claude Code auto-discovers it when launched from the repo dir.

```bash
cd rick           # if not already here
claude
```

**Verify:** inside Claude Code, run:

```
/mcp
```

You should see `rick_mcp` in the connected servers list with status **connected** (or **ready**). If
not, see [`/mcp` doesn't show rick_mcp](#mcp-doesnt-show-rick_mcp).

### Step 4 — Run a tool

```
rick_capabilities
```

**Verify:** returns the full tool map (46 tools, 36 resources organized by mission phase).

That's the minimum viable Rick. You now have an MCP server that any Claude session can query.

---

## Optional — Give Rick his soul (identity)

Without identity files, Rick uses generic defaults (`callsign: operator`, `name: Operator`, generic
tagline). To make Rick speak as **you**, populate `~/.rick_mcp/` with identity content.

The repo ships `soul-example/` — a fully worked example using a fictional operator (`sh4d0wf0x`).

```bash
# Copy the example files into your private content dir
cp soul-example/identity.yaml ~/.rick_mcp/
cp -r soul-example/soul soul-example/profiles soul-example/resume soul-example/docs ~/.rick_mcp/

# Optional: copy the vault skeleton (enables vault:// resources + engagement → vault projection)
cp -r soul-example/vault ~/.rick_mcp/

# Edit your identity — this is the core config
$EDITOR ~/.rick_mcp/identity.yaml
```

**What each file does:**

| Path                           | Powers                                                                |
|--------------------------------|-----------------------------------------------------------------------|
| `~/.rick_mcp/identity.yaml`    | Name, callsign, certs, tools, tagline — every tool reads this         |
| `~/.rick_mcp/soul/SOUL.md`     | Core principles and values — feeds `be_rick` and `dick_mode` personas |
| `~/.rick_mcp/soul/PROFILE.md`  | Current state, what's on the horizon                                  |
| `~/.rick_mcp/soul/my book.txt` | Your writing, memoirs, voice — feeds `mentor_mode`                    |
| `~/.rick_mcp/profiles/`        | 11 identity resources (stack, methodology, timeline, etc.)            |
| `~/.rick_mcp/resume/`          | 4 resume resources (overview, evidence, portfolio, contact)           |
| `~/.rick_mcp/docs/`            | War stories and additional context                                    |
| `~/.rick_mcp/vault/`           | Optional Obsidian Second Brain                                        |

**Verify** the identity loaded:

In Claude Code:

```
rick_status
```

The output should show your `callsign` and `name` from `identity.yaml`. If you see `operator` /
`Operator`, your file isn't being read.
See [identity.yaml silently using defaults](#identityyaml-silently-using-defaults).

---

## Optional — Run from a Kali VM

If you do engagements from Kali, mirror your host `~/.rick_mcp/` into the guest at the same logical
path. Engagement notes typed in Kali sync to the host instantly — Obsidian indexes them live.

### Prereq (one-time, on the macOS host)

VMware Fusion → Virtual Machine → Settings → Sharing:

1. Enable **Shared Folders**
2. Click **+** and add `~/.rick_mcp`
3. Name the share **exactly** `rick_mcp` (case-sensitive)
4. If the VM was running when you added the share, restart the VM

### Verify the share is visible in Kali

```bash
vmware-hgfsclient
```

Should list `rick_mcp`. If it returns empty, the host-side share wasn't configured correctly — go back
to the prereq.

### Run the mount script

```bash
bash scripts/setup_kali_mount.sh
```

The script is idempotent (safe to re-run). It:

1. Installs `open-vm-tools-desktop` if missing
2. Preflights `vmware-hgfsclient` to confirm the share is visible
3. Creates `/home/kali/.rick_mcp` and chowns it
4. Adds an fstab entry (idempotent — matches by mount point, not full line)
5. Mounts the share
6. Runs a round-trip write test

**Verify:**

```bash
ls /home/kali/.rick_mcp/    # should show soul/ profiles/ vault/ identity.yaml ...
touch /home/kali/.rick_mcp/.test-write && rm /home/kali/.rick_mcp/.test-write
```

If the round-trip succeeds, edit engagement notes in Kali at
`/home/kali/.rick_mcp/vault/Engagements/<codename>.md` — host Obsidian indexes the change live.

**Non-VMware platforms:** swap `fuse.vmhgfs-fuse` for the guest-tools driver of VirtualBox / Parallels /
UTM. See the script header for details.

---

## Optional — Claude Desktop

If you'd rather use Claude Desktop than Claude Code, add this to your MCP config at
`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rick_mcp": {
      "command": "python",
      "args": [
        "/absolute/path/to/rick/rick_mcp.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/rick` with your actual clone path (typically `~/IdeaProjects/rick` or
`~/work/rick`).

**Verify:** restart Claude Desktop. Open settings → MCP → you should see `rick_mcp` listed as
connected. Then in a chat, run `rick_capabilities`.

---

## Optional — Docker

```bash
docker build -t rick_mcp .
docker run rick_mcp
```

The Docker image runs the standalone server (`python rick_mcp.py`). Wiring Docker-hosted Rick to a
Claude client is platform-specific — see the Dockerfile + MCP transport docs.

---

## Troubleshooting

### `make setup` fails

**Symptom:** `make setup` errors out partway through.

**Diagnose:**

```bash
which python3 && python3 --version    # need 3.10+
which make && make --version
```

If Python is wrong: install a newer version (Homebrew: `brew install python@3.12`). Then **remove the
existing venv** and retry:

```bash
rm -rf venv
make setup
```

If `pip install` errors with permission denied, your shell is using global Python instead of the venv.
Activate the venv first: `source venv/bin/activate`.

### `make test` errors with `ImportError`

**Symptom:** Tests fail immediately with `ModuleNotFoundError` or `ImportError`.

**Cause:** the venv is missing or deps weren't installed into it. The Makefile targets use
`venv/bin/pytest` directly, so if the venv is incomplete, tests can't find their deps.

**Fix:** re-run `make setup` — it's idempotent and will populate the venv.

```bash
make setup
make test
```

If the issue persists, blow away the venv and start clean:

```bash
rm -rf venv
make setup
make test
```

### `/mcp` doesn't show rick_mcp

**Symptom:** Inside Claude Code, `/mcp` runs but `rick_mcp` isn't in the list.

**Diagnose:**

```bash
# Are you in the right directory?
pwd                                    # should be inside the rick repo
test -f .mcp.json && echo ".mcp.json present"

# Is the server even valid?
source venv/bin/activate
python rick_mcp.py --help 2>&1 | head -5    # should not error
```

**Common causes:**

- Claude Code was launched from outside the repo (no `.mcp.json` to discover). Restart Claude Code with
  `cd rick && claude`.
- `.mcp.json` references a Python path that doesn't exist. Open `.mcp.json` and verify the `command`
    + `args` paths are correct for your machine.
- The venv isn't activated and Claude Code is using global Python that's missing FastMCP. Activate the
  venv before launching Claude Code, or update `.mcp.json` to point at `venv/bin/python` directly.

### `identity.yaml` silently using defaults

**Symptom:** `rick_status` shows `callsign: operator`, `name: Operator` instead of your customized
values.

**Diagnose:**

```bash
ls -la ~/.rick_mcp/identity.yaml    # exists?
python3 -c "import yaml; print(yaml.safe_load(open('$HOME/.rick_mcp/identity.yaml')))"
```

**Common causes:**

- `~/.rick_mcp/identity.yaml` doesn't exist. Copy it: `cp soul-example/identity.yaml ~/.rick_mcp/`.
- The YAML is malformed. The loader falls back to generic defaults silently (with a log line — check
  `~/.rick_mcp/logs/` or stderr). The `python3 -c` command above will raise on malformed YAML.
- `pyyaml` isn't installed in the running Python. With the venv active: `pip install pyyaml`.

### Pre-commit hook fails on commit

**Symptom:** `git commit` aborts with hook output showing files were modified.

**Fix:** the hook fixed the files automatically. **Re-stage** and create a **NEW commit** — never
`--amend` (that rewrites previous commits and can destroy in-progress work).

```bash
git add <the files the hook modified>
git commit -m "..."
```

This is documented as Operating Discipline Rule #3 in [`CLAUDE.md`](CLAUDE.md).

### Kali mount: silent broken state

**Symptom:** `setup_kali_mount.sh` runs to "[+] mounted" but then `ls /home/kali/.rick_mcp` returns
`No such file or directory`.

**Cause:** the fstab entry parsed and `mount` exited 0, but `vmhgfs-fuse` can't reach the host share
(usually because the host-side VMware shared folder isn't configured, or the share name doesn't
match).

**Fix:** the latest version of the script catches this with a preflight check. Make sure you're on
the latest commit. Then:

```bash
# Clean up the broken mount
sudo umount /home/kali/.rick_mcp 2>/dev/null
sudo fusermount -u /home/kali/.rick_mcp 2>/dev/null
sudo systemctl daemon-reload

# Verify the host-side share
vmware-hgfsclient    # should list 'rick_mcp'

# Re-run
bash scripts/setup_kali_mount.sh
```

If `vmware-hgfsclient` still returns empty after the host-side config, restart the Kali VM.

### `rick_capabilities` errors

**Symptom:** Tool runs but errors out instead of returning the tool map.

**Diagnose:** check the Claude Code MCP logs for the actual error trace. Common causes:

- Missing dep in the venv (re-run `make setup`)
- Identity loader crash on malformed `~/.rick_mcp/identity.yaml` (see
  [identity.yaml silently using defaults](#identityyaml-silently-using-defaults) — but in this case
  the loader is hard-failing instead of falling back, which means a code change broke the fallback
  path — open an issue)

---

## Next steps

Rick is running. Now what?

- **Try a tool with real input.** `rick_recon` for `web_app` target. `rick_vuln_assess` for
  `injection`. `rick_cheatsheet` for `nmap`. Full catalog: `rick_capabilities`.
- **Start a kill chain.** `rick_kill_chain action=list` shows active engagements; `action=create`
  starts one.
- **Explore the skills.** The repo ships project-local Claude Code skills under `.claude/skills/`.
  See [`.claude/skills/SKILLS.md`](.claude/skills/SKILLS.md) for the catalog. Try `/engagement-kickoff`
  or `/arsenal-report`.
- **Read the methodology.** `profile://methodology` or the [README §
  Tools](README.md#tools--46-functional-tools).
- **Customize Rick's voice.** Edit `~/.rick_mcp/soul/SOUL.md`, `~/.rick_mcp/profiles/mantras.md`, and
  `~/.rick_mcp/identity.yaml`. Rick reloads from these at every call.

The tools are the craft. The identity is yours.
