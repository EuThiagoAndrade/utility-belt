"""Testes para o adaptador e ferramentas Docker."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from utility_belt.cli import app
from utility_belt.tools.docker_export.main import main as docker_export_main

runner = CliRunner()


def test_docker_export_dry_run(tmp_path: Path) -> None:
    target = tmp_path / "teste.tar"
    result = runner.invoke(app, ["docker", "export", "-i", "alpine:latest", "-o", str(target), "--dry-run"])
    assert result.exit_code == 0
    assert "[DRY-RUN] Simulação concluída" in result.output
    # Garante que nenhum arquivo real foi criado na simulação
    assert not target.exists()


def test_docker_import_dry_run(tmp_path: Path) -> None:
    fake_tar = tmp_path / "backup.tar"
    fake_tar.write_text("dummy tar content")

    result = runner.invoke(app, ["docker", "import", "-i", str(fake_tar), "--dry-run"])
    assert result.exit_code == 0
    assert "[DRY-RUN] Validação concluída" in result.output


def test_docker_export_atomic_promotion(tmp_path: Path) -> None:
    target = tmp_path / "meu_export.tar"

    def fake_subprocess_run(cmd, *args, **kwargs):
        # cmd: ["docker", "save", "-o", str(temp_tar), "nginx:alpine"]
        assert cmd[0] == "docker"
        assert cmd[1] == "save"
        temp_tar_path = Path(cmd[3])
        temp_tar_path.write_text("conteudo docker tar simulado")
        proc = MagicMock()
        proc.returncode = 0
        return proc

    with patch("sys.argv", ["docker_export", "-i", "nginx:alpine", "-o", str(target)]):
        with patch("subprocess.run", side_effect=fake_subprocess_run):
            code = docker_export_main()
            assert code == 0
            assert target.is_file()
            assert target.with_suffix(".txt").is_file()
            assert not target.with_name(f"{target.stem}.tmp.tar").exists()
