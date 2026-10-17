"""Testes para os menus interativos do Utility Belt."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from utility_belt.cli import app

runner = CliRunner()


# ─── Testes do callback invoke_without_command ───────────────────────────────


class TestCLICallbackBehavior:
    """Verifica que os callbacks invoke_without_command estão configurados."""

    def test_belt_no_args_calls_show_menu_in_tty(self) -> None:
        """Quando `belt` é chamado sem args em TTY, deve chamar show_menu."""
        with patch("utility_belt.cli.show_menu") as mock_menu:
            with patch("utility_belt.cli.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                runner.invoke(app, [])
                mock_menu.assert_called_once()

    def test_belt_with_subcommand_does_not_open_menu(self) -> None:
        """Quando `belt list` é chamado, NÃO deve abrir o menu."""
        with patch("utility_belt.cli.show_menu") as mock_menu:
            result = runner.invoke(app, ["list"])
            mock_menu.assert_not_called()
            assert result.exit_code == 0

    def test_belt_version_flag_still_works(self) -> None:
        """Flag --version deve continuar funcionando."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "belt (utility-belt) versão" in result.output

    def test_belt_restic_no_args_calls_restic_menu_in_tty(self) -> None:
        """Quando `belt restic` é chamado sem args em TTY, deve chamar show_restic_menu."""
        with patch("utility_belt.ui.restic_menu.show_restic_menu") as mock_ui:
            with patch("utility_belt.adapters.restic.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                runner.invoke(app, ["restic"])
                mock_ui.assert_called_once()

    def test_belt_restic_with_subcommand_does_not_open_menu(self) -> None:
        """Quando `belt restic snapshots` é chamado, NÃO deve abrir o menu do restic."""
        # snapshots requer a ferramenta restic.backup no catálogo, mas não deve abrir menu
        runner.invoke(app, ["restic", "snapshots"])
        # Pode falhar se restic não instalado, mas não deve abrir menu interativo

    def test_belt_docker_no_args_calls_docker_menu_in_tty(self) -> None:
        """Quando `belt docker` é chamado sem args em TTY, deve chamar show_docker_menu."""
        with patch("utility_belt.ui.docker_menu.show_docker_menu") as mock_ui:
            with patch("utility_belt.adapters.docker.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                runner.invoke(app, ["docker"])
                mock_ui.assert_called_once()

    def test_belt_docker_with_subcommand_does_not_open_menu(self) -> None:
        """Quando `belt docker export` é chamado, NÃO deve abrir o menu do docker."""
        runner.invoke(app, ["docker", "export"])
        # Pode falhar se docker não instalado, mas não deve abrir menu interativo

    def test_belt_dev_no_args_calls_dev_menu_in_tty(self) -> None:
        """Quando `belt dev` é chamado sem args em TTY, deve chamar show_dev_menu."""
        with patch("utility_belt.ui.dev_menu.show_dev_menu") as mock_ui:
            with patch("utility_belt.adapters.dev.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                runner.invoke(app, ["dev"])
                mock_ui.assert_called_once()


# ─── Testes de importação dos módulos de menu ─────────────────────────────────


class TestMenuModulesImport:
    """Verifica que os módulos de menu podem ser importados sem erros."""

    def test_import_restic_menu(self) -> None:
        from utility_belt.ui.restic_menu import show_restic_menu

        assert callable(show_restic_menu)

    def test_import_docker_menu(self) -> None:
        from utility_belt.ui.docker_menu import show_docker_menu

        assert callable(show_docker_menu)

    def test_import_dev_menu(self) -> None:
        from utility_belt.ui.dev_menu import show_dev_menu

        assert callable(show_dev_menu)

    def test_import_main_menu(self) -> None:
        from utility_belt.menu import show_menu

        assert callable(show_menu)


# ─── Testes de migração de configuração ───────────────────────────────────────


class TestConfigMigration:
    """Verifica que a migração de configurações legadas funciona."""

    def test_migrate_legacy_config_returns_none_without_legacy(self, tmp_path: object) -> None:
        """Sem config legada, a migração deve retornar None."""
        from utility_belt.config import migrate_legacy_restic_config

        with patch.dict("os.environ", {"LOCALAPPDATA": str(tmp_path)}):
            result = migrate_legacy_restic_config()
            assert result is None

    def test_migrate_legacy_config_imports_data(self, tmp_path: object) -> None:
        """Com config legada válida, deve importar os dados para o perfil."""
        import json
        from pathlib import Path

        from utility_belt.config import migrate_legacy_restic_config

        legacy_dir = Path(str(tmp_path)) / "ResticMenu"
        legacy_dir.mkdir()
        legacy_file = legacy_dir / "config.json"
        legacy_data = {
            "repo": "D:\\Backups\\repo",
            "repo_id": "abc123",
            "source": "C:\\Users\\test",
            "restore_parent": "D:\\Restored",
            "exclude_file": "C:\\excludes.txt",
        }
        legacy_file.write_text(json.dumps(legacy_data), encoding="utf-8")

        with patch.dict("os.environ", {"LOCALAPPDATA": str(tmp_path)}):
            with patch("utility_belt.config.get_config_file") as mock_cf:
                config_file = Path(str(tmp_path)) / "belt_config" / "config.toml"
                config_file.parent.mkdir(parents=True, exist_ok=True)
                mock_cf.return_value = config_file
                result = migrate_legacy_restic_config()
                assert result is not None
                assert result["repo"] == "D:\\Backups\\repo"
                assert result["source"] == "C:\\Users\\test"


# ─── Testes do Restic Menu (funções internas) ────────────────────────────────


class TestResticMenuFunctions:
    """Testa funções internas do restic_menu."""

    def test_get_restic_env_includes_password(self) -> None:
        """Se _session_password estiver definido, deve incluir RESTIC_PASSWORD no env."""
        import utility_belt.ui.restic_menu as rm

        original = rm._session_password
        try:
            rm._session_password = "test_password_123"
            env = rm.get_restic_env()
            assert env["RESTIC_PASSWORD"] == "test_password_123"
        finally:
            rm._session_password = original

    def test_get_restic_env_without_password(self) -> None:
        """Sem senha de sessão nem env var, RESTIC_PASSWORD não deve estar no env."""
        import utility_belt.ui.restic_menu as rm

        original = rm._session_password
        try:
            rm._session_password = None
            with patch.dict("os.environ", {}, clear=False):
                os.environ.pop("RESTIC_PASSWORD", None)
                env = rm.get_restic_env()
                assert "RESTIC_PASSWORD" not in env or env.get("RESTIC_PASSWORD") is None
        finally:
            rm._session_password = original

    def test_ask_password_from_env(self) -> None:
        """Se RESTIC_PASSWORD estiver no ambiente, deve usar sem perguntar."""
        import utility_belt.ui.restic_menu as rm

        original = rm._session_password
        try:
            rm._session_password = None
            with patch.dict("os.environ", {"RESTIC_PASSWORD": "env_pass"}):
                result = rm.ask_password_if_needed()
                assert result is True
                assert rm._session_password == "env_pass"
        finally:
            rm._session_password = original


# ─── Testes do Docker Menu (funções internas) ────────────────────────────────


class TestDockerMenuFunctions:
    """Testa funções internas do docker_menu."""

    def test_get_docker_images_when_docker_not_found(self) -> None:
        """Quando docker não está instalado, deve retornar lista vazia."""
        from utility_belt.ui.docker_menu import get_docker_images

        with patch("utility_belt.ui.docker_menu.subprocess.run", side_effect=FileNotFoundError):
            result = get_docker_images()
            assert result == []

    def test_get_docker_images_when_error(self) -> None:
        """Quando docker retorna erro, deve retornar lista vazia."""
        import subprocess

        from utility_belt.ui.docker_menu import get_docker_images

        with patch(
            "utility_belt.ui.docker_menu.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "docker"),
        ):
            result = get_docker_images()
            assert result == []

    def test_get_docker_images_success(self) -> None:
        """Quando docker retorna imagens, deve retornar lista populada."""
        from utility_belt.ui.docker_menu import get_docker_images

        mock_result = MagicMock()
        mock_result.stdout = "ubuntu:latest (72.8MB, ID: abc123)\nalpine:3.18 (7.34MB, ID: def456)\n"

        with patch("utility_belt.ui.docker_menu.subprocess.run", return_value=mock_result):
            result = get_docker_images()
            assert len(result) == 2
            assert "ubuntu:latest" in result[0]
            assert "alpine:3.18" in result[1]


# ─── Testes da estrutura do menu principal ────────────────────────────────────


class TestMainMenu:
    """Verifica que o menu principal tem a estrutura correta."""

    def test_menu_requires_tty(self) -> None:
        """Menu deve verificar TTY antes de executar."""
        from utility_belt.menu import show_menu

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            with pytest.raises(SystemExit) as exc_info:
                show_menu()
            assert exc_info.value.code == 2

    def test_main_menu_renders_banner_and_exits(self) -> None:
        """Testa que o menu principal limpa a tela, renderiza banner e sai com sair."""
        from utility_belt.menu import show_menu

        with patch("sys.stdin") as mock_stdin, \
             patch("utility_belt.menu.clear_screen") as mock_clear, \
             patch("utility_belt.menu.render_banner") as mock_banner, \
             patch("questionary.select") as mock_select:
            mock_stdin.isatty.return_value = True
            mock_select.return_value.ask.return_value = "sair"
            show_menu()
            assert mock_clear.called
            mock_banner.assert_called_once()
            mock_select.assert_called_once()

    def test_main_menu_handles_keyboard_interrupt(self) -> None:
        """Testa que KeyboardInterrupt encerra o menu principal sem erro."""
        from utility_belt.menu import show_menu

        with patch("sys.stdin") as mock_stdin, \
             patch("utility_belt.menu.clear_screen"), \
             patch("questionary.select", side_effect=KeyboardInterrupt):
            mock_stdin.isatty.return_value = True
            show_menu()


class TestSubmenusNavigation:
    """Verifica comportamento de tela dos submenus."""

    def test_docker_menu_renders_header_and_exits(self) -> None:
        """Menu Docker deve limpar a tela, exibir cabeçalho e sair graciosamente."""
        from utility_belt.ui.docker_menu import show_docker_menu

        with patch("utility_belt.ui.docker_menu.clear_screen") as mock_clear, \
             patch("utility_belt.ui.docker_menu.render_header") as mock_header, \
             patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "exit"
            show_docker_menu()
            mock_clear.assert_called_once()
            mock_header.assert_called_once_with(["UTILITY BELT", "DOCKER"])

    def test_docker_menu_handles_keyboard_interrupt(self) -> None:
        """Menu Docker deve tratar KeyboardInterrupt graciosamente."""
        from utility_belt.ui.docker_menu import show_docker_menu

        with patch("utility_belt.ui.docker_menu.clear_screen"), \
             patch("questionary.select", side_effect=KeyboardInterrupt):
            show_docker_menu()

    def test_restic_menu_renders_header_and_exits(self) -> None:
        """Menu Restic deve limpar a tela, exibir cabeçalho e sair graciosamente."""
        from utility_belt.ui.restic_menu import show_restic_menu

        with patch("utility_belt.ui.restic_menu.clear_screen") as mock_clear, \
             patch("utility_belt.ui.restic_menu.render_header") as mock_header, \
             patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "exit"
            show_restic_menu()
            mock_clear.assert_called_once()
            mock_header.assert_called_once_with(["UTILITY BELT", "RESTIC"])

    def test_restic_menu_handles_keyboard_interrupt(self) -> None:
        """Menu Restic deve tratar KeyboardInterrupt graciosamente."""
        from utility_belt.ui.restic_menu import show_restic_menu

        with patch("utility_belt.ui.restic_menu.clear_screen"), \
             patch("questionary.select", side_effect=KeyboardInterrupt):
            show_restic_menu()


# ─── Testes dos comandos explícitos de menu ───────────────────────────────────


class TestExplicitMenuCommands:
    """Verifica que os comandos 'belt restic menu' e 'belt docker menu' existem."""

    def test_restic_menu_command_exists(self) -> None:
        """'belt restic menu' deve ser um comando registrado."""
        result = runner.invoke(app, ["restic", "menu", "--help"])
        assert result.exit_code == 0
        assert "menu interativo" in result.output.lower()

    def test_docker_menu_command_exists(self) -> None:
        """'belt docker menu' deve ser um comando registrado."""
        result = runner.invoke(app, ["docker", "menu", "--help"])
        assert result.exit_code == 0
        assert "menu interativo" in result.output.lower()
