#!/usr/bin/env python3
"""(Re)bake the local `rick` Ollama model from the single-source persona.

Renders ``rick_mcp.prompts.build_ollama_system()`` — the lean, local-model-tuned Rick
persona assembled from ``~/.rick_mcp/`` soul + identity — and pushes it to an Ollama host
via ``/api/create``, swapping only the SYSTEM prompt. Deriving ``from`` an existing model
inherits its base weights, template, and tuned parameters, so a re-bake changes only the
persona.

Nothing is written to disk: the rendered persona (which carries operator identity) lives
only in memory and on the Ollama host. Generic + forkable — a fork with no ``identity.yaml``
bakes the neutral operator persona; edit the soul, re-run, the model reflects it.

    python scripts/build_rick_ollama.py --print                  # preview the persona, no push
    python scripts/build_rick_ollama.py --dry-run                # show the create request, no push
    python scripts/build_rick_ollama.py --model-name rick-test   # bake a throwaway tag first
    python scripts/build_rick_ollama.py                          # bake `rick` on $RICK_HOST
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rick_mcp.prompts import build_ollama_system  # noqa: E402  (path bootstrap must precede import)

# Generic default — the standard Ollama endpoint. Point at a remote/LAN box with $RICK_HOST
# (kept in your environment, never hardcoded here).
DEFAULT_HOST = os.environ.get("RICK_HOST", "http://localhost:11434")

# Sampling tuned for reliable MCP tool-calling. Explicit (not just inherited) so a re-bake is
# reproducible and a forker deriving from a bare base model still gets sane sampling.
# NOTE: no presence_penalty — a high value corrupts the structured tool-call format and causes
# language drift on some bases (observed on qwen2.5: it skipped the tool and hallucinated a path).
DEFAULT_PARAMS: dict = {
    "temperature": 0.5,
    "num_ctx": 16384,
    "top_k": 20,
    "top_p": 0.9,
    "repeat_penalty": 1.05,
}


def create_request(system: str, from_model: str, model_name: str, params: dict | None = None) -> dict:
    """Build the Ollama ``/api/create`` request body (structured create API)."""
    return {
        "model": model_name,
        "from": from_model,
        "system": system,
        "parameters": dict(params if params is not None else DEFAULT_PARAMS),
        "stream": False,
    }


def post_create(host: str, body: dict, timeout: int = 300) -> list[dict]:
    """POST to ``{host}/api/create`` and return the parsed status messages.

    Raises ``RuntimeError`` if Ollama reports a create error, or ``urllib.error.URLError``
    if the host is unreachable. The response is newline-delimited JSON status lines.
    """
    url = host.rstrip("/") + "/api/create"
    req = urllib.request.Request(  # noqa: S310  (host is operator-controlled; http/https by construction)
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    messages: list[dict] = []
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        raw = resp.read().decode()
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        messages.append(msg)
        if "error" in msg:
            raise RuntimeError(f"Ollama create failed: {msg['error']}")
    return messages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="(Re)bake the local `rick` Ollama model from the single-source persona."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Ollama host (default: {DEFAULT_HOST} / $RICK_HOST)")
    parser.add_argument("--model-name", default="rick", help="Target model tag to create (default: rick)")
    parser.add_argument(
        "--from",
        dest="from_model",
        default="rick",
        help="Model to derive from — inherits its base/template/params (default: rick, an in-place "
        "persona swap). Forkers: pass your base model, e.g. qwen3.6:latest.",
    )
    parser.add_argument("--print", action="store_true", dest="print_only", help="Print the persona and exit (no push)")
    parser.add_argument("--dry-run", action="store_true", help="Print the create request (persona elided) and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    system = build_ollama_system()

    if args.print_only:
        print(system)
        return 0

    body = create_request(system, args.from_model, args.model_name)

    if args.dry_run:
        preview = dict(body)
        preview["system"] = f"<{len(system)} chars>"
        print(json.dumps(preview, indent=2))
        return 0

    print(
        f"Baking '{args.model_name}' from '{args.from_model}' on {args.host} ({len(system)} chars of persona)...",
        file=sys.stderr,
    )
    try:
        post_create(args.host, body)
    except (urllib.error.URLError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"✓ Baked '{args.model_name}'. Try: OLLAMA_HOST={args.host} ollama run {args.model_name} \"who are you?\"",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
