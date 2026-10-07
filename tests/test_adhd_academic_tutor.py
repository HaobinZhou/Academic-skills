"""Check tutor memory setup, preservation, and rejection of unusable state."""

import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "adhd-academic-tutor" / "scripts"


def run(script, memory):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--memory-dir", str(memory)],
        capture_output=True, text=True,
    )


@pytest.fixture
def memory(tmp_path):
    path = tmp_path / "private learner memory"
    result = run("init_memory.py", path)
    assert result.returncode == 0, result.stderr
    return path


def test_fresh_memory_validates_and_reinitialization_preserves_work(memory):
    assert run("validate_memory.py", memory).returncode == 0
    profile = memory / "user_cognitive_profile.md"
    profile.write_text(profile.read_text() + "\nLearner-owned note.\n")
    asset = memory / "assets" / "paper.pdf"
    asset.write_bytes(b"saved learner source")
    before = {p.relative_to(memory): p.read_bytes() for p in memory.rglob("*") if p.is_file()}
    assert run("init_memory.py", memory).returncode == 0
    assert before == {p.relative_to(memory): p.read_bytes() for p in memory.rglob("*") if p.is_file()}
    assert run("validate_memory.py", memory).returncode == 0


def test_missing_idea_inbox_is_rejected(memory):
    (memory / "research_idea_inbox.md").unlink()
    result = run("validate_memory.py", memory)
    assert result.returncode == 1
    assert "missing required file" in result.stderr


def test_renamed_achievement_section_is_rejected(memory):
    path = memory / "achievement_log.md"
    path.write_text(path.read_text().replace("## Unlocked Achievements", "## Achievements"))
    result = run("validate_memory.py", memory)
    assert result.returncode == 1
    assert "missing canonical heading" in result.stderr


def test_legacy_manifest_is_rejected_without_overwriting_it(memory):
    path = memory / "memory_manifest.json"
    data = json.loads(path.read_text())
    data["schema"] = "adhd-academic-tutor-memory-v1"
    path.write_text(json.dumps(data))
    before = path.read_bytes()
    result = run("validate_memory.py", memory)
    assert result.returncode == 1
    assert "manifest schema" in result.stderr
    assert path.read_bytes() == before


def test_missing_indexed_source_asset_is_rejected(memory):
    path = memory / "reading_backlog_master.md"
    header = "| id | created_at | source | local_path | why_saved |\n| --- | --- | --- | --- | --- |"
    path.write_text(path.read_text().replace(
        header, header + f"\n| source-1 | 2026-10-07 | Paper figure | {memory / 'assets' / 'missing.png'} | Review |",
    ))
    result = run("validate_memory.py", memory)
    assert result.returncode == 1
    assert "indexed asset path does not exist" in result.stderr
