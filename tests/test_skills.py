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
    assert body["data"]["skills"][0]["name"] == "typesafe-ai"


def test_skills_install_offline(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["skills", "install", "--offline", "--target", "grok", "--project"])
    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    skill = tmp_path / ".agents" / "skills" / "typesafe-ai" / "SKILL.md"
    note = tmp_path / ".agents" / "skills" / "typesafe-ai" / "CLI.md"
    assert skill.is_file()
    assert note.is_file()
    assert "typesafe-ai" in skill.read_text(encoding="utf-8")
    assert "typesafe ask" in note.read_text(encoding="utf-8")
    assert str(skill) in body["data"]["written"]


def test_skills_install_dir_override(tmp_path: Path):
    dest = tmp_path / "custom-skills"
    result = runner.invoke(
        app,
        ["skills", "install", "--offline", "--dir", str(dest)],
    )
    assert result.exit_code == 0, result.output
    assert (dest / "typesafe-ai" / "SKILL.md").is_file()
