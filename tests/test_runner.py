"""Testes para o executor (runner) do Utility Belt."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from utility_belt.catalog import ToolManifest
from utility_belt.runner import (
    EXIT_INTERRUPTED,
    EXIT_PRECONDITION_FAILED,
    resolve_runtime_command,
    run_tool,
)


def test_resolve_runtime_command_python(tmp_path: Path) -> None:
    entry = tmp_path / "main.py"
    entry.write_text("print('hello')")

    manifest = ToolManifest(
        id="test.py",
        name="Test",
        description="",
        runtime="python",
        entry="main.py",
        platforms=["windows", "linux"],
        tool_dir=tmp_path,
    )

    cmd = resolve_runtime_command(manifest, ["--flag", "valor"])
    assert cmd[0] == sys.executable
    assert cmd[1] == str(entry)
    assert cmd[2:] == ["--flag", "valor"]


def test_run_tool_incompatible_platform(tmp_path: Path) -> None:
    manifest = ToolManifest(
        id="test.other_os",
        name="Other OS",
        description="",
        runtime="python",
        entry="main.py",
        platforms=["freebsd"],  # Incompatível
        tool_dir=tmp_path,
    )

    code = run_tool(manifest)
    assert code == EXIT_PRECONDITION_FAILED


def test_run_tool_interactive_without_tty(tmp_path: Path) -> None:
    manifest = ToolManifest(
        id="test.interactive",
        name="Interactive",
        description="",
        runtime="python",
        entry="main.py",
        platforms=["windows", "linux", "darwin"],
        interactive=True,
        tool_dir=tmp_path,
    )

    with patch("sys.stdin.isatty", return_value=False):
        code = run_tool(manifest)
        assert code == EXIT_PRECONDITION_FAILED


def test_run_tool_preserves_cwd_and_exit_code(tmp_path: Path) -> None:
    entry = tmp_path / "main.py"
    entry.write_text("import sys; sys.exit(42)")

    manifest = ToolManifest(
        id="test.exit_code",
        name="Exit Code",
        description="",
        runtime="python",
        entry="main.py",
        platforms=["windows", "linux", "darwin"],
        tool_dir=tmp_path,
    )

    mock_proc = MagicMock()
    mock_proc.returncode = 42

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        code = run_tool(manifest, args=["arg1"])
        assert code == 42
        mock_run.assert_called_once()
        # Verifica se o cwd passado ao subprocesso é o diretório atual do usuário
        _, kwargs = mock_run.call_args
        assert kwargs["cwd"] == Path.cwd()


def test_run_tool_keyboard_interrupt(tmp_path: Path) -> None:
    manifest = ToolManifest(
        id="test.interrupt",
        name="Interrupt",
        description="",
        runtime="python",
        entry="main.py",
        platforms=["windows", "linux", "darwin"],
        tool_dir=tmp_path,
    )

    with patch("utility_belt.runner.resolve_runtime_command", return_value=["mock"]):
        with patch("subprocess.run", side_effect=KeyboardInterrupt):
            code = run_tool(manifest)
            assert code == EXIT_INTERRUPTED
