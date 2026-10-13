"""Contratos CLI/menu/diagnóstico, sem aquisições ou serviços externos."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from utility_belt import config, markdown
from utility_belt.adapters import markdown as adapter
from utility_belt.catalog import catalog
from utility_belt.cli import app
from utility_belt.markdown_runtime import runtime as engine
from utility_belt.ui import markdown_menu as menu

runner = CliRunner()


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "get_config_file", lambda: tmp_path / "config.toml")
    monkeypatch.setattr(engine, "get_data_dir", lambda: tmp_path / "data")
    return tmp_path


@pytest.mark.parametrize("args,code", [(["markdown"], 0), (["markdown", "convert"], 2),
                                     (["markdown", "batch"], 2), (["markdown", "watch"], 2),
                                     (["markdown", "config"], 2), (["markdown", "menu"], 2)])
def test_no_tty_arguments_never_prompt(args, code, isolated, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("Prompt indevido"))
    result = runner.invoke(app, args)
    assert result.exit_code == code, result.output
    assert not (isolated / "data").exists()


@pytest.mark.parametrize("mode", [[], ["--non-interactive"]])
def test_missing_destination_never_prompts_even_tty(mode, isolated, monkeypatch):
    source = isolated / "file.txt"
    source.write_text("test")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("Prompt indevido"))
    result = runner.invoke(app, ["markdown", "convert", str(source), *mode])
    assert result.exit_code == 2 and "Destino ausente" in result.output


def test_config_preserves_document_and_rejects_invalid_toml(isolated):
    path = isolated / "config.toml"
    path.write_text('[profiles.existing]\nrepo="keep"\n')
    result = runner.invoke(app, ["markdown", "config", "--output-dir", str(isolated / "out")])
    assert result.exit_code == 0
    assert config.load_config()["profiles"]["existing"]["repo"] == "keep"
    original = "[broken"
    path.write_text(original)
    result = runner.invoke(app, ["markdown", "config", "--output-dir", str(isolated / "other")])
    assert result.exit_code == 2 and path.read_text() == original


@pytest.mark.parametrize("command", ["convert", "batch", "watch", "clipboard"])
def test_group_and_command_noninteractive_propagate(command, monkeypatch):
    calls = []
    result = markdown.ConversionResult(130, "cancelled", "cancelled")
    def execute(*args, **kwargs):
        calls.append(kwargs)
        return result
    if command == "watch":
        monkeypatch.setattr(adapter, "watch", execute)
    else:
        monkeypatch.setattr(markdown, command, execute)
    arguments = [] if command == "clipboard" else ["source"]
    for args in (["markdown", "--non-interactive", command, *arguments],
                 ["markdown", command, *arguments, "--non-interactive"]):
        response = runner.invoke(app, args)
        assert response.exit_code == 130, response.output
    assert all(call["non_interactive"] for call in calls)


def test_runner_flag_reaches_child_in_tty(monkeypatch):
    from utility_belt.runner import run_tool
    commands = []
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: commands.append((cmd, kw)) or
                        subprocess.CompletedProcess(cmd, 2))
    tool = catalog.get_tool("markdown.convert")
    assert tool.risk == "write" and not tool.interactive and not tool.supports_dry_run
    original = ["convert", "file.txt"]
    assert run_tool(tool, original, non_interactive=True) == 2
    assert commands[0][0][2:] == ["--non-interactive", *original]
    assert commands[0][1]["cwd"] == Path.cwd()
    assert original == ["convert", "file.txt"]


def test_runtime_recipe_and_interpreter_identity(isolated, monkeypatch):
    first = engine.Runtime(None, data_dir=isolated)
    assert first.root == engine.Runtime(None, data_dir=isolated).root
    monkeypatch.setattr(engine, "recipe_revision", lambda: "changed")
    second = engine.Runtime(None, data_dir=isolated)
    assert first.root != second.root and not first.root.exists()
    monkeypatch.setattr(engine.sys, "version_info", Mock(major=3, minor=14))
    assert second.root != engine.Runtime(None, data_dir=isolated).root


def test_doctor_does_not_create_or_install_or_read_clipboard(isolated, monkeypatch):
    from utility_belt import doctor
    monkeypatch.setattr(doctor.platformdirs, "user_data_path", lambda **_: isolated / "missing")
    monkeypatch.setattr(engine.Runtime, "ensure", lambda *_: pytest.fail("Instalação indevida"))
    import pyperclip
    monkeypatch.setattr(pyperclip, "paste", lambda: pytest.fail("Leitura indevida"))
    info = doctor.check_markdown()
    assert not info["installed"] and not (isolated / "missing").exists()
    assert "details" in doctor.check_clipboard()
    assert json.dumps(info)


def test_doctor_reports_acquired_groups_without_lock(isolated, monkeypatch):
    from utility_belt import doctor
    monkeypatch.setattr(doctor.platformdirs, "user_data_path", lambda **_: isolated)
    runtime = engine.Runtime(None, data_dir=isolated)
    runtime.python().parent.mkdir(parents=True)
    runtime.python().touch()
    monkeypatch.setattr(subprocess, "run", lambda cmd, **_: subprocess.CompletedProcess(
        cmd, 0, stdout='{"base": true, "pdf": true, "docx": false}'))
    info = doctor.check_markdown()
    assert info["installed"] and info["environments"]["core"]["groups"]["pdf"]
    assert not (runtime.root / ".lock").exists()


@pytest.mark.parametrize("code", [0, 1, 2, 130])
def test_menu_returns_after_each_outcome(code, isolated, monkeypatch):
    config.save_markdown_output_dir(isolated / "out")
    selections = iter(["convert", "exit"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(menu, "clear_screen", lambda: None)
    monkeypatch.setattr(menu, "render_header", lambda *_: None)
    monkeypatch.setattr(menu.questionary, "select", lambda *a, **k: Mock(ask=lambda: next(selections)))
    monkeypatch.setattr(menu.questionary, "text", lambda *a, **k: Mock(ask=lambda: "file.txt"))
    monkeypatch.setattr(menu, "run_dedicated_screen", lambda title, action, choice: action(choice))
    convert = Mock(return_value=markdown.ConversionResult(code, "result", "diagnostic"))
    monkeypatch.setattr(markdown, "convert", convert)
    menu.show_markdown_menu()
    convert.assert_called_once_with("file.txt")


def test_menu_missing_destination_can_cancel(isolated, monkeypatch):
    monkeypatch.setattr(menu.questionary, "path", lambda *a, **k: Mock(ask=lambda: None))
    monkeypatch.setattr(markdown, "convert", lambda *_: pytest.fail("Cancelamento ignorado"))
    menu.execute("convert")
    assert not (isolated / "config.toml").exists()


@pytest.mark.parametrize("choice", ["batch", "watch", "clipboard", "config"])
def test_menu_routes_remaining_capabilities(choice, isolated, monkeypatch):
    config.save_markdown_output_dir(isolated / "out")
    monkeypatch.setattr(menu.questionary, "path", lambda *a, **k: Mock(ask=lambda: str(isolated / "source")))
    operation = Mock(return_value=markdown.OperationResult(130, 1, 0, 0, (), "cancelled"))
    if choice == "watch":
        monkeypatch.setattr(menu, "watch", operation)
    elif choice == "config":
        monkeypatch.setattr(menu, "save_markdown_output_dir", operation)
    else:
        monkeypatch.setattr(markdown, choice, operation)
    menu.execute(choice)
    operation.assert_called_once()


def test_main_menu_routes_markdown_and_preserves_options(monkeypatch):
    from utility_belt import menu as main_menu
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(main_menu, "clear_screen", lambda: None)
    monkeypatch.setattr(main_menu, "is_banner_enabled", lambda: False)
    monkeypatch.setattr(main_menu, "render_compact_banner", lambda: None)
    choices = iter(["markdown", "sair"])
    def select(*args, **kwargs):
        values = [getattr(c, "value", None) for c in kwargs["choices"]]
        assert all(value in values for value in ("restic", "docker", "system", "markdown", "sair"))
        return Mock(ask=lambda: next(choices))
    monkeypatch.setattr(main_menu.questionary, "select", select)
    selected = Mock()
    monkeypatch.setattr(menu, "show_markdown_menu", selected)
    main_menu.show_menu()
    selected.assert_called_once()


def test_tty_menu_and_noninteractive_help(monkeypatch):
    selected = Mock()
    monkeypatch.setattr(menu, "show_markdown_menu", selected)
    monkeypatch.setattr(adapter.sys, "stdin", Mock(isatty=lambda: True))
    # CliRunner substitui stdin; testar o callback com contexto real não é necessário
    from types import SimpleNamespace
    context = SimpleNamespace(invoked_subcommand=None, obj=None, get_help=lambda: "help")
    adapter.callback(context, non_interactive=False)
    selected.assert_called_once()
    adapter.callback(context, non_interactive=True)
    selected.assert_called_once()


def test_failed_acquisition_has_code_one_and_retry_requires_new_consent(isolated, monkeypatch):
    source = isolated / "file.txt"
    source.write_text("content")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    confirmations = []
    monkeypatch.setattr("builtins.input", lambda message: confirmations.append(message) or "s")
    monkeypatch.setattr(engine.Runtime, "available", lambda *_: False)
    monkeypatch.setattr(engine.shutil, "which", lambda *_: "uv")
    def failed(args, **_):
        if args[-1] == "--version":
            return "uv 0.12.13"
        raise engine.RequirementError("simulated acquisition failure")
    monkeypatch.setattr(engine, "run_process", failed)
    for _ in range(2):
        result = markdown.convert(source, output_dir=isolated / "out")
        assert result.code == 1 and result.output is None
    assert len(confirmations) == 2


@pytest.mark.parametrize("backend", ["xclip", "xsel", "wl-clipboard"])
def test_graphical_clipboard_precedes_wsl_detection_and_restores_library(backend, monkeypatch):
    import pyperclip
    monkeypatch.setattr(markdown.sys, "platform", "linux")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("DISPLAY", ":99")
    tools = [backend]
    if backend == "wl-clipboard":
        tools = ["wl-copy", "wl-paste"]
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-test")
    monkeypatch.setattr(markdown.shutil, "which", lambda name: name if name in tools else None)
    original = pyperclip.copy, pyperclip.paste
    def select(name):
        assert name == backend
        monkeypatch.setattr(pyperclip, "paste", lambda: "local fixture")
    monkeypatch.setattr(pyperclip, "set_clipboard", select)
    assert markdown.clipboard_text() == "local fixture"
    assert (pyperclip.copy, pyperclip.paste) == original
