from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from typesafe_cli.cli import app
from typesafe_cli.commands.skills import load_official_skill

runner = CliRunner()


def test_vendored_skill_is_official():
    text = load_official_skill(offline=True)
    assert text.startswith("---")
    assert "name: typesafe-ai" in text
    assert "System One" in text


def test_skills_list():
    result = runner.invoke(app, ["skills", "list"])
    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    names = {s["name"] for s in body["data"]["skills"]}
    assert names == {"typesafe-cli", "typesafe-ai"}


def test_skills_install_offline(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["skills", "install", "--offline", "--target", "grok", "--project"])
    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    skill = tmp_path / ".agents" / "skills" / "typesafe-ai" / "SKILL.md"
    note = tmp_path / ".agents" / "skills" / "typesafe-ai" / "CLI.md"
    cli_skill = tmp_path / ".agents" / "skills" / "typesafe-cli" / "SKILL.md"
    assert skill.is_file()
    assert note.is_file()
    assert cli_skill.is_file()
    assert "typesafe-ai" in skill.read_text(encoding="utf-8")
    cli_text = cli_skill.read_text(encoding="utf-8")
    assert "You are the context adapter" in cli_text
    assert "/tmp}/codex/" in cli_text or "/codex/" in cli_text
    assert "Those paths **are** the collection list" in cli_text or "collection list" in cli_text
    assert "TYPESAFE_*" in note.read_text(encoding="utf-8")
    assert str(cli_skill) in body["data"]["written"]
    agents = tmp_path / "AGENTS.md"
    assert agents.is_file()
    text = agents.read_text(encoding="utf-8")
    assert "<!-- typesafe-cli:start -->" in text
    assert "<!-- typesafe-cli:end -->" in text
    assert "typesafe-cli" in text
    assert "investigate" in text
    assert str(agents) in body["data"]["written"]


def test_skills_install_dir_override(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dest = tmp_path / "custom-skills"
    result = runner.invoke(
        app,
        ["skills", "install", "--offline", "--dir", str(dest)],
    )
    assert result.exit_code == 0, result.output
    assert (dest / "typesafe-ai" / "SKILL.md").is_file()
    assert (dest / "typesafe-cli" / "SKILL.md").is_file()


def test_skills_install_appends_pointer_to_existing_agent_files(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    claude = tmp_path / "CLAUDE.md"
    claude.write_text("# Project\n\nDo not invent APIs.\n", encoding="utf-8")
    result = runner.invoke(app, ["skills", "install", "--offline", "--target", "claude", "--project"])
    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    text = claude.read_text(encoding="utf-8")
    assert text.startswith("# Project")
    assert "Do not invent APIs." in text
    assert "<!-- typesafe-cli:start -->" in text
    assert "investigate" in text
    assert str(claude) in body["data"]["written"]
    assert not (tmp_path / "AGENTS.md").exists()


def test_skills_install_is_idempotent_on_agent_files(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = runner.invoke(app, ["skills", "install", "--offline", "--target", "grok", "--project"])
    second = runner.invoke(app, ["skills", "install", "--offline", "--target", "grok", "--project"])
    assert first.exit_code == 0 and second.exit_code == 0
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert text.count("<!-- typesafe-cli:start -->") == 1
    assert text.count("investigate") == 1
