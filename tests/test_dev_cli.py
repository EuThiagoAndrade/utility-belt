"""Testes de interface CLI e diagnóstico para o módulo dev (Janitor e Git-Tidy)."""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from utility_belt.cli import app
from utility_belt.doctor import check_git, run_diagnostics

runner = CliRunner()


def _clean(text: str) -> str:
    """Remove sequências ANSI para asserções confiáveis em qualquer plataforma."""
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)


def test_cli_dev_help() -> None:
    result = runner.invoke(app, ["dev", "--help"], env={"NO_COLOR": "1", "TERM": "dumb"})
    assert result.exit_code == 0
    clean = _clean(result.output)
    assert "janitor" in clean
    assert "git-tidy" in clean
    assert "menu" in clean


def test_cli_dev_janitor_help() -> None:
    result = runner.invoke(app, ["dev", "janitor", "--help"], env={"NO_COLOR": "1", "TERM": "dumb"})
    assert result.exit_code == 0
    clean = _clean(result.output)
    assert "--dry-run" in clean
    assert "--days" in clean
    assert "--yes" in clean


def test_cli_dev_git_tidy_help() -> None:
    result = runner.invoke(app, ["dev", "git-tidy", "--help"], env={"NO_COLOR": "1", "TERM": "dumb"})
    assert result.exit_code == 0
    clean = _clean(result.output)
    assert "--dry-run" in clean
    assert "--remote" in clean
    assert "--all" in clean
    assert "--yes" in clean


def test_cli_dev_janitor_invalid_path() -> None:
    result = runner.invoke(app, ["dev", "janitor", "non_existent_dir_12345"])
    assert result.exit_code == 2
    assert "não é um diretório válido" in result.output


def test_cli_dev_janitor_dry_run_execution(tmp_path: Path) -> None:
    cache_dir = tmp_path / "node_modules"
    cache_dir.mkdir()
    (cache_dir / "pkg.json").write_text("{}")

    result = runner.invoke(app, ["dev", "janitor", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "node_modules" in result.output
    assert "--dry-run" in result.output
    assert cache_dir.is_dir()


def test_cli_dev_git_tidy_dry_run_local() -> None:
    with patch("utility_belt.adapters.dev.is_git_installed", return_value=True):
        with patch("utility_belt.adapters.dev.is_inside_git_repo", return_value=True):
            with patch("utility_belt.adapters.dev.prune_remote", return_value=(True, "")):
                with patch(
                    "utility_belt.adapters.dev.get_local_branches",
                    return_value=[],
                ):
                    result = runner.invoke(app, ["dev", "git-tidy", "--dry-run"])
                    assert result.exit_code == 0
                    assert "Nenhuma branch local órfã" in result.output


def test_cli_dev_menu_non_tty() -> None:
    result = runner.invoke(app, ["dev", "menu"])
    assert result.exit_code == 2
    assert "requer um terminal interativo" in result.output


def test_doctor_check_git() -> None:
    info = check_git()
    assert "installed" in info
    if info["installed"]:
        assert "git version" in info["details"].lower() or "git" in info["details"].lower()
    else:
        assert "install_guide" in info

    diagnostics = run_diagnostics()
    assert "git" in diagnostics["dependencies"]
