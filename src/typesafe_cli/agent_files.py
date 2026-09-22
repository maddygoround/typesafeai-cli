"""Idempotent pointer in project agent files so TypeSafe is reached on keywords."""

from __future__ import annotations

from pathlib import Path

START = "<!-- typesafe-cli:start -->"
END = "<!-- typesafe-cli:end -->"
AGENT_FILENAMES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")

SNIPPET = """<!-- typesafe-cli:start -->
## TypeSafe CLI

When the user asks to investigate, triage, verify a claim, rank options, extract a span, screen a message, route a task, or make a typed yes/no or score judgment (Jev, noul, choice, TypeSafe), follow the **typesafe-cli** skill and run `typesafe`. Collect only the named state first. Do not curl TypeSafe.
<!-- typesafe-cli:end -->
"""


def upsert_agent_files(root: Path) -> list[Path]:
    existing = [root / name for name in AGENT_FILENAMES if (root / name).is_file()]
    targets = existing or [root / "AGENTS.md"]
    written: list[Path] = []
    for path in targets:
        _upsert_snippet(path)
        written.append(path)
    return written


def _upsert_snippet(path: Path) -> None:
    body = path.read_text(encoding="utf-8") if path.is_file() else ""
    block = SNIPPET.strip() + "\n"
    start = body.find(START)
    end = body.find(END)
    if start != -1 and end != -1 and end > start:
        end += len(END)
        while end < len(body) and body[end] == "\n":
            end += 1
        updated = body[:start].rstrip() + "\n\n" + block + body[end:].lstrip("\n")
        if not updated.endswith("\n"):
            updated += "\n"
    elif body.strip():
        updated = body.rstrip() + "\n\n" + block
    else:
        updated = block
    path.write_text(updated, encoding="utf-8")
