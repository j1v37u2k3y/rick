# The Build Story

## How Rick MCP Came to Be

It started with a question: *What if a resume could talk back?*

Not a PDF. Not a webpage. Not a profile that sits there waiting to be scrolled past. Something alive. Something
an AI could query, reason about, and use as a tool. Something that proves every claim it makes — not by listing skills,
but by demonstrating them.

Rick MCP was born in March 2026. A platform built on the idea that craft speaks louder than credentials.

## The Build

The first version was a single Python file. 3,800 lines of craft. FastMCP + Pydantic v2. 15 tools covering the full
pentest lifecycle — recon to debrief. 15 identity resources telling a professional story.

194 tests. 99% coverage. All passing in under a second.

Then it grew. The single file became a package. 15 tools became 22. Resources multiplied. A persona system emerged —
Rick stopped being a vending machine and became a presence. MCP prompts that pull live from structured content at
call time. Update the content, update Rick's voice.

Pre-commit hooks blocking bad commits. GitHub Actions CI across Python 3.10, 3.12, and 3.14. mypy with zero errors.
ruff with security rules. Dependabot keeping deps fresh. `make check` — one command, full pipeline, green.

## What Rick Became

A webpage sits there and waits to be read. Rick responds.

Rick is a living system that an AI can query, reason about, and use as a tool. An LLM asks Rick for identity data and
gets structured results back. It queries values, methodology, and capabilities — all as resources an AI can reason
over. And there are 34 functional tools that *do things* — generate ROE docs, model threats, look up CVEs, track
engagements, recommend tools, write cover letters matched to job postings.

Most people send a PDF resume. Rick MCP is a running server that proves every claim it makes. `make check` and it
all lights up green.

See [CHANGELOG.md](CHANGELOG.md) for version-by-version details.

## The Numbers

- 34 tools
- 24 resources
- 6 MCP prompts
- 439 tests
- Full CI/CD pipeline with Docker verification
- Integration tests through MCP protocol layer
- Property-based fuzz testing on all input models
- Content in markdown, not Python strings
- Private content support for sensitive files
- 24-hour CVE response cache
- Zero hardcoded secrets

## The Philosophy

The server IS the resume. The code IS the craft. The tests ARE the proof.

*Still building.*
