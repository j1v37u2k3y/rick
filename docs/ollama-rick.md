# Rick as a Local Ollama Model

Turn your rick_mcp persona into a local LLM that *is* Rick — the soul + identity baked into an
Ollama model on your own hardware, so `ollama run rick` answers in your voice, not a generic
assistant's.

The persona is **generated, not hand-written**: `make rick-ollama` renders
`rick_mcp/prompts.py::build_ollama_system()` — the same `~/.rick_mcp/` soul + identity the MCP
server uses for `be_rick` — and pushes it to your Ollama host. Edit the soul, re-run, the model
resyncs. One source of truth; the local model and the MCP-served Rick never drift.

## Two ways to run it

1. **Raw** — `ollama run rick` — the persona, standalone. Voice, values, the mark. No tools.
2. **As an agent** — drive the model with an MCP host (e.g. [mcphost](https://github.com/mark3labs/mcphost))
   pointed at your rick_mcp server → the persona **plus** the `rick_*` tools.

## Prerequisites

- An Ollama host reachable over HTTP. Defaults to `http://localhost:11434`; point at a remote or
  LAN box by exporting `RICK_HOST` (e.g. `export RICK_HOST=http://10.0.0.5:11434`).
- A tool-capable base model pulled on that host (`qwen3.6`, `qwen2.5:14b`, `llama3.1`, …).
- This repo's venv — `make setup`.
- Optional but recommended: `~/.rick_mcp/identity.yaml` + `~/.rick_mcp/soul/SOUL.md`. Without them
  you get the **neutral operator persona** (no personalization, no PII).

## Bake it

```bash
make rick-ollama-print        # preview the persona — nothing is pushed
make rick-ollama              # render + push to $RICK_HOST, (re)creating model `rick`
```

Both wrap `scripts/build_rick_ollama.py`:

| Flag           | Default                                  | Purpose                                                                                                 |
|----------------|------------------------------------------|---------------------------------------------------------------------------------------------------------|
| `--host`       | `$RICK_HOST` or `http://localhost:11434` | Ollama host to push to                                                                                  |
| `--model-name` | `rick`                                   | Target model tag to create                                                                              |
| `--from`       | `rick`                                   | Model to derive from — inherits its base weights, template, and tuned params (an in-place persona swap) |
| `--print`      | —                                        | Print the persona and exit (no push)                                                                    |
| `--dry-run`    | —                                        | Print the create request (persona elided) and exit                                                      |

**First bake** (no `rick` model exists yet) — derive from your base model:

```bash
python scripts/build_rick_ollama.py --from qwen3.6:latest
```

**Re-bake** after editing your soul — in-place, preserves the tuned params:

```bash
make rick-ollama
```

Nothing is written to disk. The rendered persona (which carries your identity) lives only in
memory and on your Ollama host — never in this repo.

## Wire it to an agent (optional — adds the tools)

`ollama run rick` gives you the voice but no tools. For the full agent — persona **and** the
`rick_*` tools — drive the model with an MCP host.

`~/.config/rick/mcphost.json`:

```json
{
  "mcpServers": {
    "rick": {
      "type": "local",
      "command": "/path/to/rick/venv/bin/python",
      "args": [
        "/path/to/rick/rick_mcp.py"
      ]
    }
  }
}
```

A `rick` launcher on your `PATH`:

```bash
#!/usr/bin/env bash
set -euo pipefail
exec mcphost \
  --config "$HOME/.config/rick/mcphost.json" \
  -m ollama:rick \
  --provider-url "${RICK_HOST:-http://localhost:11434}" \
  "$@"
```

**One caveat about system prompts:** `ollama run rick` always uses the baked persona. An MCP host,
however, may send its *own* tool-aware system prompt, which can override the model's `SYSTEM` for
that session. If your host does and you want the full persona there too, emit it to a file and hand
it to the host's system-prompt option:

```bash
python scripts/build_rick_ollama.py --print > /tmp/rick.system && \
  mcphost --system-prompt /tmp/rick.system ...   # that file carries your identity — keep it local
```

## Privacy

The baked persona contains whatever your `identity.yaml` / soul say. It lives on **your** Ollama
host, never in this repo. The generator is generic — a fork with no identity files bakes the
neutral operator persona.
