"""Formatting and utility helpers for rick_mcp."""

import json
import logging
from functools import wraps
from pathlib import Path

from rick_mcp.constants import ResponseFormat

logger = logging.getLogger("rick_mcp")


def _fmt(data: dict, fmt: ResponseFormat, title: str = "") -> str:
    """Format tool output as markdown or JSON."""
    if fmt == ResponseFormat.JSON:
        return json.dumps(data, indent=2, default=str)
    lines = []
    if title:
        lines += [f"# {title}", ""]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"## {key.replace('_', ' ').title()}")
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        lines.append(f"- **{k}**: {v}")
                    lines.append("")
                else:
                    lines.append(f"- {item}")
            lines.append("")
        elif isinstance(value, dict):
            lines.append(f"## {key.replace('_', ' ').title()}")
            for k, v in value.items():
                if isinstance(v, list):
                    lines.append(f"**{k.replace('_', ' ').title()}:**")
                    for i in v:
                        lines.append(f"- {i}")
                else:
                    lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")
            lines.append("")
        else:
            lines += [f"**{key.replace('_', ' ').title()}**: {value}", ""]
    return "\n".join(lines)


def _sanitize(value: str | None) -> str | None:
    """Strip null bytes and control characters from user input."""
    if value is None:
        return None
    return value.replace("\x00", "").strip()


def _safe_tool(fn):
    """Decorator that wraps tool functions in try/except. Logs calls and errors."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        logger.info(f"Tool called: {fn.__name__}")
        try:
            return await fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool {fn.__name__} failed: {e}")
            return f"Error: {fn.__name__} encountered an issue: {e}"

    return wrapper


def _read_md(filename: str) -> str:
    """Read a markdown file from the project root."""
    path = Path(__file__).parent.parent / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"{filename} not found."


def _read_data(category: str, name: str) -> str:
    """Read a markdown file from rick_mcp/data/{category}/{name}.md."""
    path = Path(__file__).parent / "data" / category / f"{name}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"Data file {category}/{name}.md not found."
