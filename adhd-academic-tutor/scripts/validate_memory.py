#!/usr/bin/env python3
"""Validate ADHD Academic Tutor memory structure."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


DEFAULT_MEMORY_DIR = Path.home() / ".adhd-academic-tutor" / "memory"
SCHEMA = "adhd-academic-tutor-memory-v2"

REQUIRED_FILES = [
    "user_cognitive_profile.md",
    "academic_knowledge_graph.md",
    "reading_backlog_master.md",
    "research_idea_inbox.md",
    "achievement_log.md",
    "session_context.json",
    "memory_manifest.json",
]
REQUIRED_DIRS = ["assets"]

CANONICAL_TABLES = {
    "achievement_log.md": [
        (
            "## Unlocked Achievements",
            "| id | created_at | achievement | evidence | why_it_matters | related_skill | next_unlock |",
        ),
    ],
    "reading_backlog_master.md": [
        (
            "## Pending Broad Survey Papers",
            "| id | paper | topic | reason | status | next_segment |",
        ),
        (
            "## Pending Deep-Reading Papers",
            "| id | paper | segment | reason | time_range | status |",
        ),
        (
            "## Completed Source Segments",
            "| id | paper | segment | completed_at | evidence | achievement_id |",
        ),
        (
            "## Local Source Assets",
            "| id | created_at | source | local_path | why_saved |",
        ),
        (
            "## Skipped or Deferred",
            "| id | paper | reason | revisit_condition |",
        ),
        (
            "## Source Reading Log",
            "| id | created_at | paper | segment | assigned_range | actual_duration | completion | friction | next_action |",
        ),
    ],
    "research_idea_inbox.md": [
        (
            "## Raw Ideas",
            "| id | created_at | idea | why_it_matters | evidence_so_far | status | next_check |",
        ),
        (
            "## Promising Ideas",
            "| id | created_at | idea | why_it_matters | evidence_so_far | status | next_check |",
        ),
        (
            "## Deferred Ideas",
            "| id | created_at | idea | why_it_matters | evidence_so_far | status | next_check |",
        ),
        (
            "## Converted Ideas",
            "| id | created_at | converted_to | evidence | status |",
        ),
    ],
    "academic_knowledge_graph.md": [
        ("## Topic Curriculum", None),
        ("## Concept Mastery", "| id | concept | evidence | confidence | status | next_action |"),
        ("## Deep Reading Bank", "| id | paper | segment | why_it_matters | writing_move | status | next_action |"),
        ("## Writing Pattern Bank", None),
        ("## Supervisor-Ready Talking Points", "| id | talking_point | source | evidence | status |"),
    ],
}

SESSION_CONTEXT_KEYS = {
    "active_mode",
    "active_paper_id",
    "assigned_segment",
    "assigned_time_range",
    "start_time",
    "soft_checkin_due",
    "pending_validation",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--memory-dir",
        default=os.environ.get("ADHD_TUTOR_MEMORY_DIR", str(DEFAULT_MEMORY_DIR)),
        help="Directory for local tutor memory. Defaults to ADHD_TUTOR_MEMORY_DIR or ~/.adhd-academic-tutor/memory.",
    )
    return parser.parse_args()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def find_line(lines: list[str], text: str) -> int | None:
    for idx, line in enumerate(lines):
        if line.strip() == text:
            return idx
    return None


def validate_required(memory_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        path = memory_dir / name
        if not path.is_file():
            errors.append(f"missing required file: {path}")
    for name in REQUIRED_DIRS:
        path = memory_dir / name
        if not path.is_dir():
            errors.append(f"missing required directory: {path}")
    return errors


def validate_manifest(memory_dir: Path) -> list[str]:
    errors: list[str] = []
    path = memory_dir / "memory_manifest.json"
    if not path.exists():
        return errors
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid memory_manifest.json: {exc}"]

    if data.get("schema") != SCHEMA:
        errors.append(f"manifest schema should be {SCHEMA}, got {data.get('schema')!r}")

    listed = set(data.get("files", []))
    expected = set(REQUIRED_FILES + ["assets/"])
    missing = sorted(expected - listed)
    if missing:
        errors.append(f"manifest missing entries: {', '.join(missing)}")
    return errors


def validate_session_context(memory_dir: Path) -> list[str]:
    path = memory_dir / "session_context.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid session_context.json: {exc}"]

    errors: list[str] = []
    missing = sorted(SESSION_CONTEXT_KEYS - set(data))
    extra = sorted(set(data) - SESSION_CONTEXT_KEYS)
    if missing:
        errors.append(f"session_context.json missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"session_context.json has unexpected keys: {', '.join(extra)}")
    if "pending_validation" in data and not isinstance(data["pending_validation"], bool):
        errors.append("session_context.json pending_validation must be boolean")
    return errors


def validate_markdown_tables(memory_dir: Path) -> list[str]:
    errors: list[str] = []
    for filename, specs in CANONICAL_TABLES.items():
        path = memory_dir / filename
        if not path.exists():
            continue
        lines = read_lines(path)
        for heading, table_header in specs:
            idx = find_line(lines, heading)
            if idx is None:
                errors.append(f"{filename} missing canonical heading: {heading}")
                continue
            if table_header is None:
                continue
            search_window = [line.strip() for line in lines[idx + 1 : idx + 8]]
            if table_header not in search_window:
                errors.append(f"{filename} heading {heading!r} missing table header: {table_header}")
    return errors


def validate_asset_index(memory_dir: Path) -> list[str]:
    path = memory_dir / "reading_backlog_master.md"
    if not path.exists():
        return []

    lines = read_lines(path)
    heading_idx = find_line(lines, "## Local Source Assets")
    if heading_idx is None:
        return []

    errors: list[str] = []
    for line in lines[heading_idx + 3 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|") or stripped.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 5:
            errors.append(f"Local Source Assets row should have 5 columns: {stripped}")
            continue
        local_path = cells[3]
        if local_path and local_path.startswith("/") and not Path(local_path).exists():
            errors.append(f"indexed asset path does not exist: {local_path}")
    return errors


def main() -> int:
    args = parse_args()
    memory_dir = Path(args.memory_dir).expanduser().resolve()
    errors = []
    errors.extend(validate_required(memory_dir))
    errors.extend(validate_manifest(memory_dir))
    errors.extend(validate_session_context(memory_dir))
    errors.extend(validate_markdown_tables(memory_dir))
    errors.extend(validate_asset_index(memory_dir))

    if errors:
        print("Memory validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Memory validation passed: {memory_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
