"""Testes dedicados para o menu interativo Restic e recuperação assistida."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import utility_belt.ui.restic_menu as rm


@pytest.fixture(autouse=True)
def reset_session_password():
    original = rm._session_password
    rm._session_password = "test-password"
    yield
    rm._session_password = original


def test_do_unlock_not_configured():
    with patch("utility_belt.ui.restic_menu.get_profile", return_value={"restic": {}}), \
         patch("utility_belt.ui.restic_menu.status_message") as mock_status:
        rm.do_unlock()
        mock_status.assert_called_with("Repositório não configurado.", fg=rm.typer.colors.RED)


def test_do_unlock_cancelled_by_user():
    profile = {"restic": {"repo": "D:\\backup_repo"}}
    with patch("utility_belt.ui.restic_menu.get_profile", return_value=profile), \
         patch("utility_belt.ui.restic_menu.prompt", return_value=False), \
         patch("utility_belt.ui.restic_menu._execute_restic") as mock_exec, \
         patch("utility_belt.ui.restic_menu.status_message") as mock_status:
        rm.do_unlock()
        mock_exec.assert_not_called()
        assert any("cancelada" in str(c) for c in mock_status.call_args_list)


def test_do_unlock_confirmed_success():
    profile = {"restic": {"repo": "D:\\backup_repo"}}
    proc = MagicMock(returncode=0, stderr="", stdout="")
    with patch("utility_belt.ui.restic_menu.get_profile", return_value=profile), \
         patch("utility_belt.ui.restic_menu.prompt", return_value=True), \
         patch("utility_belt.ui.restic_menu._execute_restic", return_value=proc) as mock_exec, \
         patch("utility_belt.ui.restic_menu.status_message") as mock_status:
        rm.do_unlock()
        mock_exec.assert_called_once_with(["-r", "D:\\backup_repo", "unlock"], capture_output=False)
        assert any("removidos com sucesso" in str(c) for c in mock_status.call_args_list)


def test_run_restic_code_11_user_retries_with_retry_lock():
    failed_proc = MagicMock(returncode=11, stderr="repository is locked")
    success_proc = MagicMock(returncode=0, stderr="", stdout="")

    executed_args = []

    def fake_execute(args, **kwargs):
        executed_args.append(args)
        if "--retry-lock" in args:
            return success_proc
        return failed_proc

    with patch("utility_belt.ui.restic_menu._execute_restic", side_effect=fake_execute), \
         patch("utility_belt.ui.restic_menu.prompt", return_value="retry"):
        res = rm.run_restic(["-r", "D:\\repo", "backup", "C:\\dados"])
        assert res.returncode == 0
        assert any("--retry-lock" in args and "1m" in args for args in executed_args)


def test_run_restic_code_11_user_executes_unlock_preserves_code_11():
    failed_proc = MagicMock(returncode=11, stderr="repository is locked")
    unlock_proc = MagicMock(returncode=0, stderr="", stdout="")

    executed_args = []

    def fake_execute(args, **kwargs):
        executed_args.append(args)
        if "unlock" in args:
            return unlock_proc
        return failed_proc

    # prompt returns "unlock" for select, and True for confirmation
    prompts = iter(["unlock", True])

    with patch("utility_belt.ui.restic_menu._execute_restic", side_effect=fake_execute), \
         patch("utility_belt.ui.restic_menu.prompt", side_effect=lambda *args, **kwargs: next(prompts)), \
         patch("utility_belt.ui.restic_menu.status_message") as mock_status:
        res = rm.run_restic(["-r", "D:\\repo", "backup", "C:\\dados"])
        # Original code 11 is preserved and not automatically repeated
        assert res.returncode == 11
        assert any("unlock" in args for args in executed_args)
        assert any("Locks obsoletos removidos com sucesso" in str(c) for c in mock_status.call_args_list)


def test_run_restic_code_11_user_chooses_back():
    failed_proc = MagicMock(returncode=11, stderr="repository is locked")

    with patch("utility_belt.ui.restic_menu._execute_restic", return_value=failed_proc) as mock_exec, \
         patch("utility_belt.ui.restic_menu.prompt", return_value="back"):
        res = rm.run_restic(["-r", "D:\\repo", "snapshots"])
        assert res.returncode == 11
        # Only the snapshots command was run, unlock was not run
        assert mock_exec.call_count == 1


def test_run_restic_unlock_failure_no_recursive_unlock():
    failed_unlock = MagicMock(returncode=11, stderr="cannot unlock: lock active")

    with patch("utility_belt.ui.restic_menu._execute_restic", return_value=failed_unlock) as mock_exec, \
         patch("utility_belt.ui.restic_menu.prompt") as mock_prompt, \
         patch("utility_belt.ui.restic_menu.status_message") as mock_status:
        res = rm.run_restic(["-r", "D:\\repo", "unlock"])
        assert res.returncode == 11
        # Prompt should not be called to offer unlock again!
        mock_prompt.assert_not_called()
        assert mock_exec.call_count == 1
        assert any("Falha ao obter lock" in str(c) for c in mock_status.call_args_list)


def test_do_restore_success_offers_explorer():
    snapshots = [{"id": "abcdef123456", "time": "2026-11-03T10:00:00Z", "paths": ["C:\\dados"]}]
    success_proc = MagicMock(returncode=0, stderr="", stdout="")

    with patch("utility_belt.ui.restic_menu.get_snapshots", return_value=snapshots), \
         patch("utility_belt.ui.restic_menu.get_profile", return_value={"restic": {"repo": "D:\\repo"}}), \
         patch("utility_belt.ui.restic_menu.prompt", side_effect=["abcdef123456", "D:\\restored", "", True]), \
         patch("utility_belt.ui.restic_menu.run_restic", return_value=success_proc), \
         patch("utility_belt.ui.restic_menu.os.startfile") as mock_startfile:
        rm.do_restore()
        mock_startfile.assert_called_once_with("D:\\restored")


def test_do_restore_failure_does_not_offer_explorer():
    snapshots = [{"id": "abcdef123456", "time": "2026-11-03T10:00:00Z", "paths": ["C:\\dados"]}]
    failed_proc = MagicMock(returncode=1, stderr="ignoring error for /dados/foo: err", stdout="")

    with patch("utility_belt.ui.restic_menu.get_snapshots", return_value=snapshots), \
         patch("utility_belt.ui.restic_menu.get_profile", return_value={"restic": {"repo": "D:\\repo"}}), \
         patch("utility_belt.ui.restic_menu.prompt", side_effect=["abcdef123456", "D:\\restored", ""]), \
         patch("utility_belt.ui.restic_menu.run_restic", return_value=failed_proc), \
         patch("utility_belt.ui.restic_menu.os.startfile") as mock_startfile, \
         patch("utility_belt.ui.restic_menu.status_message") as mock_status:
        rm.do_restore()
        # Must not offer or open explorer!
        mock_startfile.assert_not_called()
        assert any("não pôde ser confirmada como completa" in str(c) for c in mock_status.call_args_list)


def test_show_restic_menu_routes_to_unlock():
    with patch("utility_belt.ui.restic_menu.clear_screen"), \
         patch("utility_belt.ui.restic_menu.render_header"), \
         patch("utility_belt.ui.restic_menu.prompt", side_effect=["unlock", "exit"]), \
         patch("utility_belt.ui.restic_menu.run_dedicated_screen") as mock_screen:
        rm.show_restic_menu()
        mock_screen.assert_called_once_with(["UTILITY BELT", "RESTIC", "DESBLOQUEIO"], rm.do_unlock)
