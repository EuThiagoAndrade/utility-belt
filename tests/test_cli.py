"""Testes para a interface de linha de comando (CLI) do Utility Belt."""

import json

from typer.testing import CliRunner

from utility_belt.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "belt (utility-belt) versão" in result.output


def test_cli_list() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "system.info" in result.output
    assert "docker.export" in result.output
    assert "restic.backup" in result.output


def test_cli_list_json() -> None:
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert "system.info" in ids


def test_cli_doctor() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Diagnóstico do Utility Belt" in result.output
    assert "Dependências Externas" in result.output


def test_cli_doctor_json() -> None:
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "system" in data
    assert "dependencies" in data


def test_cli_run_system_info() -> None:
    result = runner.invoke(app, ["run", "system.info", "--", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "sistema" in data
    assert "python" in data


def test_cli_show_completion() -> None:
    result = runner.invoke(app, ["show-completion", "powershell"])
    assert result.exit_code == 0
    assert "Register-ArgumentCompleter" in result.output
