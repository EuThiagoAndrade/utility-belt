"""Testes automatizados para a validação prévia de dependências (preflight guard)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from utility_belt.ui.guard import (
    DEPENDENCY_INFO,
    check_dependency_installed,
    ensure_dependency,
    open_download_page,
    show_dependency_guard,
    show_docker_daemon_guard,
    show_installation_instructions,
)


def test_check_dependency_installed() -> None:
    with patch("shutil.which", return_value="C:\\Program Files\\restic\\restic.exe"):
        assert check_dependency_installed("restic") is True

    with patch("shutil.which", return_value=None):
        assert check_dependency_installed("restic") is False

    # Dependência desconhecida retorna True por segurança
    assert check_dependency_installed("unknown_tool") is True


def test_ensure_dependency_non_interactive(capsys) -> None:
    with patch("sys.stdin.isatty", return_value=False):
        with patch("utility_belt.ui.guard.check_dependency_installed", return_value=True):
            assert ensure_dependency("restic") is True

        with patch("utility_belt.ui.guard.check_dependency_installed", return_value=False):
            assert ensure_dependency("restic") is False
            captured = capsys.readouterr()
            assert "Dependência 'Restic' não está instalada" in captured.err


def test_ensure_dependency_restic_installed() -> None:
    with patch("sys.stdin.isatty", return_value=True):
        with patch("utility_belt.ui.guard.check_dependency_installed", return_value=True):
            assert ensure_dependency("restic") is True


def test_ensure_dependency_restic_missing_user_exits() -> None:
    with patch("sys.stdin.isatty", return_value=True):
        with patch("utility_belt.ui.guard.check_dependency_installed", return_value=False):
            with patch("utility_belt.ui.guard.prompt", return_value="exit"):
                assert ensure_dependency("restic") is False


def test_show_installation_instructions_windows() -> None:
    mock_ask = MagicMock()
    with patch("sys.stdin.isatty", return_value=True):
        with patch("sys.platform", "win32"):
            with patch("questionary.press_any_key_to_continue") as mock_press:
                mock_press.return_value.ask = mock_ask
                show_installation_instructions("restic")
                assert mock_ask.called


def test_show_installation_instructions_linux() -> None:
    mock_ask = MagicMock()
    with patch("sys.stdin.isatty", return_value=True):
        with patch("sys.platform", "linux"):
            with patch("questionary.press_any_key_to_continue") as mock_press:
                mock_press.return_value.ask = mock_ask
                show_installation_instructions("docker")
                assert mock_ask.called


def test_open_download_page() -> None:
    mock_ask = MagicMock()
    with patch("sys.stdin.isatty", return_value=True):
        with patch("webbrowser.open", return_value=True) as mock_open:
            with patch("questionary.press_any_key_to_continue") as mock_press:
                mock_press.return_value.ask = mock_ask
                open_download_page("restic")
                mock_open.assert_called_once_with(DEPENDENCY_INFO["restic"]["download_url"])
                assert mock_ask.called


def test_show_dependency_guard_flow() -> None:
    # Simula o usuário selecionando ver instruções e depois saindo
    responses = iter(["instructions", "exit"])
    with patch("utility_belt.ui.guard.prompt", side_effect=responses):
        with patch("utility_belt.ui.guard.show_installation_instructions") as mock_inst:
            result = show_dependency_guard("restic")
            assert mock_inst.called
            assert result is False


def test_ensure_dependency_docker_installed_and_daemon_running() -> None:
    with patch("sys.stdin.isatty", return_value=True):
        with patch("utility_belt.ui.guard.check_dependency_installed", return_value=True):
            with patch("utility_belt.doctor.check_docker", return_value={"installed": True, "daemon_running": True}):
                assert ensure_dependency("docker") is True


def test_ensure_dependency_docker_daemon_stopped_user_exits() -> None:
    with patch("sys.stdin.isatty", return_value=True):
        with patch("utility_belt.ui.guard.check_dependency_installed", return_value=True):
            with patch("utility_belt.doctor.check_docker", return_value={"installed": True, "daemon_running": False}):
                with patch("utility_belt.ui.guard.prompt", return_value="exit"):
                    assert ensure_dependency("docker") is False


def test_docker_daemon_guard_retry_success() -> None:
    responses = iter(["retry"])
    with patch("utility_belt.ui.guard.prompt", side_effect=responses):
        with patch("utility_belt.doctor.check_docker", return_value={"installed": True, "daemon_running": True}):
            assert show_docker_daemon_guard() is True
