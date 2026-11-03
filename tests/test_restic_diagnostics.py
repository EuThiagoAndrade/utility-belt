"""Testes para o módulo restic_diagnostics."""

from __future__ import annotations

from utility_belt.restic_diagnostics import (
    diagnose_restic_result,
    format_cli_guidance,
    format_menu_guidance,
)


def test_diagnose_success_returns_none() -> None:
    assert diagnose_restic_result("backup", 0) is None
    assert diagnose_restic_result("restore", 0) is None
    assert diagnose_restic_result("unlock", 0) is None


def test_diagnose_code_11_lock_failure() -> None:
    diag = diagnose_restic_result("backup", 11)
    assert diag is not None
    assert diag.returncode == 11
    assert "Falha ao obter lock" in diag.summary
    assert "belt restic unlock" in diag.guidance

    diag_snap = diagnose_restic_result("snapshots", 11)
    assert diag_snap is not None
    assert "belt restic unlock" in diag_snap.guidance


def test_diagnose_backup_code_3_incomplete() -> None:
    diag = diagnose_restic_result("backup", 3)
    assert diag is not None
    assert diag.returncode == 3
    assert "incompleto" in diag.summary.lower()
    assert "não puderam ser lidos" in diag.guidance


def test_diagnose_restore_with_extracted_path_and_detail() -> None:
    stderr = (
        "restic restore started\n"
        "ignoring error for C:\\dados\\arquivo_sumido.txt: SetFileTime: The system cannot find the file specified.\n"
        "There were 1 errors\n"
    )
    diag = diagnose_restic_result("restore", 1, stderr=stderr)
    assert diag is not None
    assert diag.returncode == 1
    assert "não pôde ser confirmada como completa" in diag.guidance
    assert diag.affected_item == "C:\\dados\\arquivo_sumido.txt"
    assert "SetFileTime" in str(diag.detail)


def test_diagnose_restore_without_path() -> None:
    diag = diagnose_restic_result("restore", 1, stderr="fatal error during restore")
    assert diag is not None
    assert diag.returncode == 1
    assert "não pôde ser confirmada como completa" in diag.guidance
    assert diag.affected_item is None


def test_diagnose_unknown_exit_code() -> None:
    diag = diagnose_restic_result("check", 99)
    assert diag is not None
    assert diag.returncode == 99
    assert "código de erro 99" in diag.summary
    assert "saída do Restic exibidas acima" in diag.guidance


def test_format_cli_guidance() -> None:
    diag = diagnose_restic_result("restore", 1, stderr="ignoring error for /tmp/item.txt: permission denied")
    assert diag is not None
    cli_text = format_cli_guidance(diag)
    assert "[DIAGNÓSTICO RESTIC]" in cli_text
    assert "/tmp/item.txt" in cli_text
    assert "permission denied" in cli_text
    assert "não pôde ser confirmada como completa" in cli_text


def test_format_menu_guidance() -> None:
    diag = diagnose_restic_result("restore", 1, stderr="ignoring error for /tmp/item.txt: permission denied")
    assert diag is not None
    menu_text = format_menu_guidance(diag)
    assert "Item afetado: /tmp/item.txt" in menu_text
    assert "Detalhe: permission denied" in menu_text
