"""Testes para o adaptador e ferramentas Restic."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from utility_belt.cli import app
from utility_belt.tools.restic_backup.main import main as restic_main
from utility_belt.tools.restic_backup.main import overlaps

runner = CliRunner()


@pytest.fixture(autouse=True)
def simulated_restic(monkeypatch):
    """Estes testes simulam Restic; não dependem de instalação no host/CI."""
    monkeypatch.setattr("utility_belt.tools.restic_backup.main.shutil.which", lambda _: "restic-test")


def test_restic_missing_binary_is_reported(tmp_path, monkeypatch):
    source, repo = tmp_path / "source", tmp_path / "repo"
    source.mkdir()
    repo.mkdir()
    monkeypatch.setattr("utility_belt.tools.restic_backup.main.shutil.which", lambda _: None)
    result = runner.invoke(app, ["restic", "backup", "--source", str(source), "--repo", str(repo)])
    assert result.exit_code == 2
    assert "Executável 'restic' não encontrado" in result.output


def test_overlaps_detection(tmp_path: Path) -> None:
    parent = tmp_path / "projetos"
    child = parent / "subpasta"
    outside = tmp_path / "outro"

    parent.mkdir()
    child.mkdir()
    outside.mkdir()

    # Mesma pasta
    assert overlaps(parent, parent) is True
    # Pai e filho
    assert overlaps(parent, child) is True
    assert overlaps(child, parent) is True
    # Pastas irmãs
    assert overlaps(parent, outside) is False


def test_restic_backup_blocks_overlap(tmp_path: Path) -> None:
    source = tmp_path / "dados"
    repo = source / "repo_dentro"  # Sobreposto!

    source.mkdir()
    repo.mkdir()

    result = runner.invoke(app, ["restic", "backup", "--source", str(source), "--repo", str(repo)])
    assert result.exit_code == 2
    assert "estão sobrepostos" in result.output


def test_restic_backup_missing_repo(tmp_path: Path) -> None:
    source = tmp_path / "origem"
    source.mkdir()
    fake_repo = tmp_path / "repo_nao_existe"

    # Simula getpass para não travar teste se chegar lá
    with patch("getpass.getpass", return_value="senha123"):
        result = runner.invoke(app, ["restic", "backup", "--source", str(source), "--repo", str(fake_repo)])
        assert result.exit_code == 2
        assert "Repositório inexistente ou inacessível" in result.output


def test_restic_backup_non_interactive_without_password(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "origem"
    repo = tmp_path / "repo"
    source.mkdir()
    repo.mkdir()
    (repo / "config").write_text("mock config")

    monkeypatch.delenv("RESTIC_PASSWORD", raising=False)

    result = runner.invoke(
        app,
        ["restic", "backup", "--source", str(source), "--repo", str(repo), "--non-interactive"],
    )
    assert result.exit_code == 2
    assert "RESTIC_PASSWORD não foi informada" in result.output


def test_restic_backup_repo_id_mismatch(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "origem"
    repo = tmp_path / "repo"
    source.mkdir()
    repo.mkdir()
    (repo / "config").write_text("dummy")

    monkeypatch.setenv("RESTIC_PASSWORD", "segredo")

    # Mock restic cat config retornando outro ID
    def fake_subprocess_run(cmd, *args, **kwargs):
        proc = MagicMock()
        if "cat" in cmd and "config" in cmd:
            proc.returncode = 0
            proc.stdout = json.dumps({"id": "id-do-disco-xyz-999"})
        return proc

    # Configura perfil com esperado diferente
    profile_data = {
        "restic": {
            "repo": str(repo),
            "repo_id": "id-esperado-diferente-123",
            "source": str(source),
        }
    }

    with patch("utility_belt.tools.restic_backup.main.get_profile", return_value=profile_data):
        with patch("subprocess.run", side_effect=fake_subprocess_run):
            with patch("sys.argv", ["restic_backup", "backup", "--profile", "teste"]):
                code = restic_main()
                assert code == 2


def test_restic_backup_code_3_incomplete(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "origem"
    repo = tmp_path / "repo"
    source.mkdir()
    repo.mkdir()
    (repo / "config").write_text("dummy")

    monkeypatch.setenv("RESTIC_PASSWORD", "segredo")

    def fake_subprocess_run(cmd, *args, **kwargs):
        proc = MagicMock()
        if "cat" in cmd and "config" in cmd:
            proc.returncode = 0
            proc.stdout = json.dumps({"id": "mesmo-id"})
        elif "backup" in cmd:
            # Simula código 3 do Restic (backup incompleto / locked files)
            proc.returncode = 3
        return proc

    profile_data = {
        "restic": {
            "repo": str(repo),
            "repo_id": "mesmo-id",
            "source": str(source),
        }
    }

    with patch("utility_belt.tools.restic_backup.main.get_profile", return_value=profile_data):
        with patch("subprocess.run", side_effect=fake_subprocess_run):
            with patch("sys.argv", ["restic_backup", "backup", "--profile", "teste"]):
                code = restic_main()
                # Preserva código 3 de backup incompleto
                assert code == 3
