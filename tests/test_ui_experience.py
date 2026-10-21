"""Contratos de navegação e apresentação sem operações externas."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from utility_belt import __version__, menu
from utility_belt.adapters.markdown import report
from utility_belt.markdown import Consent, ConversionResult, OperationResult
from utility_belt.ui import screen


@pytest.mark.parametrize("choice,action", [("doctor", "_show_diagnostics"),
                                          ("sysinfo", "_run_system_info"), ("about", "_show_about")])
def test_system_routes_and_returns(choice, action, monkeypatch):
    monkeypatch.setattr(menu, "clear_screen", lambda: None)
    monkeypatch.setattr(menu, "render_header", lambda *_: None)
    selections = iter([choice, "exit"])
    def select(*_, **kwargs):
        assert [c.value for c in kwargs["choices"] if not isinstance(c, menu.questionary.Separator)] == ["doctor", "sysinfo", "about", "exit"]
        return Mock(ask=lambda: next(selections))
    monkeypatch.setattr(menu.questionary, "select", select)
    run = Mock()
    monkeypatch.setattr(menu, "run_dedicated_screen", run)
    menu.show_system_menu()
    assert run.call_count == 1 and run.call_args.args[1] == getattr(menu, action)


def test_about_uses_package_version(capsys):
    menu._show_about()
    assert __version__ in capsys.readouterr().out


@pytest.mark.parametrize("width", [20, 40, 80, 120])
def test_header_fits_width_without_color(width, monkeypatch, capsys):
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setattr(screen, "get_terminal_width", lambda: width)
    screen.render_banner()
    screen.render_header(["UTILITY BELT", "Markdown", "Converter arquivo ou URL"])
    output = capsys.readouterr().out
    assert "\033" not in output
    assert all(len(line) <= width for line in output.splitlines())


def test_redirect_does_not_clear_or_color(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(screen.os, "system", lambda *_: pytest.fail("Limpeza indevida"))
    screen.clear_screen()
    screen.message("SUCESSO", "Pronto")
    assert "\033" not in capsys.readouterr().out


def test_message_separates_unterminated_output(capsys):
    print("Saída anterior", end="")
    screen.message("AVISO", "Verifique o destino")
    output = capsys.readouterr().out
    assert "Saída anterior\n[AVISO]" in output


def test_prompt_separates_tool_output(monkeypatch, capsys):
    print("Saída da ferramenta", end="")
    def factory(text, **kwargs):
        assert capsys.readouterr().out.endswith("Saída da ferramenta\n")
        assert text == "Continuar?" and "style" in kwargs
        return Mock(ask=lambda: False)
    assert screen.prompt(factory, "Continuar?") is False


def test_confirmation_explanation_is_separate_and_default_negative(monkeypatch, capsys):
    prompts = []
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "")
    print("Anterior", end="")
    assert not Consent._ask("Instala componentes para converter PDF.")
    assert prompts == ["Deseja autorizar esta ação? [s/N] "]
    assert "Anterior\n[CONFIRMAÇÃO]\nInstala" in capsys.readouterr().out


@pytest.mark.parametrize("status,code,label", [("success", 0, "SUCESSO"), ("partial", 1, "AVISO"),
                                              ("failed", 1, "ERRO"), ("unavailable", 2, "AVISO"),
                                              ("cancelled", 130, "CANCELADO")])
def test_conversion_result_has_readable_status(status, code, label, capsys):
    report(ConversionResult(code, status, "diagnóstico", Path("out.md") if code == 0 else None))
    output = capsys.readouterr().out
    assert f"[{label}]" in output and status not in output
    if code == 0:
        assert "Salvo em: out.md" in output


def test_batch_summary_preserves_cancellation(capsys):
    report(OperationResult(130, 2, 1, 3, (), "Resultados anteriores preservados"))
    output = capsys.readouterr().out
    assert "[CANCELADO]" in output
    assert "Convertidos: 2 | Com erro: 1 | Ignorados: 3" in output


def test_result_visible_until_return_confirmation(monkeypatch, capsys):
    monkeypatch.setattr(screen, "clear_screen", lambda: None)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    def pause(*args, **kwargs):
        assert "Resultado final" in capsys.readouterr().out
        return Mock(ask=lambda: None)
    monkeypatch.setattr(screen.questionary, "press_any_key_to_continue", pause)
    screen.run_dedicated_screen("Converter", lambda: print("Resultado final"))


# ─── Testes do Ciclo 010 (Compatibilidade de Opções e Separadores) ────────────


def test_menu_options_does_not_contain_use_shortcuts():
    """menu_options() não deve conter 'use_shortcuts' para segurança com checkboxes."""
    assert "use_shortcuts" not in screen.menu_options()


def test_prompt_real_checkbox_with_menu_options():
    """Instanciação real de questionary.checkbox com menu_options() não levanta TypeError."""
    import questionary
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    with create_pipe_input() as inp:
        inp.send_text(" \r")
        result = screen.prompt(
            questionary.checkbox,
            "Selecione:",
            choices=["item1", "item2"],
            input=inp,
            output=DummyOutput(),
            **screen.menu_options(),
        )
        assert result == ["item1"]


def test_prompt_defensive_guard_discards_use_shortcuts_for_checkbox():
    """A guarda defensiva em screen.prompt() remove 'use_shortcuts' quando a fábrica não o suporta."""
    import questionary
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    with create_pipe_input() as inp:
        inp.send_text(" \r")
        result = screen.prompt(
            questionary.checkbox,
            "Selecione:",
            choices=["item1", "item2"],
            use_shortcuts=False,
            input=inp,
            output=DummyOutput(),
        )
        assert result == ["item1"]


def test_prompt_real_select_with_menu_options_non_regression():
    """questionary.select real continua funcionando normalmente com menu_options()."""
    import questionary
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    with create_pipe_input() as inp:
        inp.send_text("\r")
        result = screen.prompt(
            questionary.select,
            "Escolha:",
            choices=["op1", "op2"],
            input=inp,
            output=DummyOutput(),
            **screen.menu_options(),
        )
        assert result == "op1"


def test_run_git_tidy_local_flow_with_eligible_branch(monkeypatch):
    """Fluxo local de git-tidy com branch elegível executa checklist real sem falha de use_shortcuts."""
    from unittest.mock import patch

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    from utility_belt.dev.git_tidy import LocalBranchInfo
    from utility_belt.ui import dev_menu

    branch = LocalBranchInfo(name="feat/eligible", is_current=False, is_protected=False, is_merged=True, is_gone=False)
    with patch("utility_belt.ui.dev_menu._check_git_environment", return_value=True), \
         patch("utility_belt.ui.dev_menu.prune_remote"), \
         patch("utility_belt.ui.dev_menu.get_local_branches", return_value=[branch]), \
         patch("utility_belt.ui.dev_menu.delete_local_branches", return_value={"feat/eligible": (True, "")}) as mock_del:
        with create_pipe_input() as inp:
            inp.send_text("\ry")
            with create_app_session(input=inp, output=DummyOutput()):
                dev_menu.run_git_tidy_local_flow()
        mock_del.assert_called_once_with(["feat/eligible"])


def test_run_git_tidy_remote_flow_with_eligible_branch(monkeypatch):
    """Fluxo remoto de git-tidy com branch elegível executa checklist real sem falha de use_shortcuts."""
    from unittest.mock import patch

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    from utility_belt.dev.git_tidy import RemoteBranchInfo
    from utility_belt.ui import dev_menu

    branch = RemoteBranchInfo(name="origin/feat/eligible", full_ref="refs/remotes/origin/feat/eligible", is_protected=False, is_merged=True)
    with patch("utility_belt.ui.dev_menu._check_git_environment", return_value=True), \
         patch("utility_belt.ui.dev_menu.prune_remote"), \
         patch("utility_belt.ui.dev_menu.get_remote_branches", return_value=[branch]), \
         patch("utility_belt.ui.dev_menu.delete_remote_branches", return_value={"origin/feat/eligible": (True, "")}) as mock_del:
        with create_pipe_input() as inp:
            inp.send_text("\ry")
            with create_app_session(input=inp, output=DummyOutput()):
                dev_menu.run_git_tidy_remote_flow()
        mock_del.assert_called_once_with(["origin/feat/eligible"])


def test_run_janitor_flow_with_eligible_cache(monkeypatch):
    """Fluxo do Janitor com cache elegível executa checklist real sem falha de use_shortcuts."""
    from unittest.mock import patch

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    from utility_belt.dev.janitor import DiscoveredCache
    from utility_belt.ui import dev_menu

    cache = DiscoveredCache(Path("dummy/cache"), "cache", 2048, 0.0, False)
    with patch("utility_belt.ui.dev_menu.scan_caches", return_value=[cache]), \
         patch("utility_belt.ui.dev_menu.delete_cache", return_value=(True, "")) as mock_del:
        with create_pipe_input() as inp:
            inp.send_text("\r\ry")
            with create_app_session(input=inp, output=DummyOutput()):
                dev_menu.run_janitor_flow()
        mock_del.assert_called_once_with(cache.path)


def test_markdown_menu_has_separator_before_exit(monkeypatch):
    """show_markdown_menu() posiciona Separator imediatamente antes da opção de saída [0]."""
    import questionary

    from utility_belt.ui import markdown_menu

    monkeypatch.setattr(markdown_menu.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(markdown_menu, "clear_screen", lambda: None)
    captured_choices = []

    def fake_select(*args, **kwargs):
        captured_choices.extend(kwargs.get("choices", []))
        return Mock(ask=lambda: "exit")

    monkeypatch.setattr(markdown_menu.questionary, "select", fake_select)
    markdown_menu.show_markdown_menu()

    exit_idx = next(i for i, c in enumerate(captured_choices) if getattr(c, "value", None) == "exit")
    assert exit_idx > 0
    assert isinstance(captured_choices[exit_idx - 1], questionary.Separator)


def test_dev_menu_has_separator_before_exit(monkeypatch):
    """show_dev_menu() posiciona Separator imediatamente antes da opção de saída [0]."""
    import questionary

    from utility_belt.ui import dev_menu

    monkeypatch.setattr(dev_menu.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(dev_menu, "clear_screen", lambda: None)
    captured_choices = []

    def fake_select(*args, **kwargs):
        captured_choices.extend(kwargs.get("choices", []))
        return Mock(ask=lambda: "exit")

    monkeypatch.setattr(dev_menu.questionary, "select", fake_select)
    dev_menu.show_dev_menu()

    exit_idx = next(i for i, c in enumerate(captured_choices) if getattr(c, "value", None) == "exit")
    assert exit_idx > 0
    assert isinstance(captured_choices[exit_idx - 1], questionary.Separator)


def test_janitor_flow_preselects_all_caches_including_active():
    """run_janitor_flow() pré-seleciona todos os caches (checked=True), mesmo ativos recentemente."""
    from unittest.mock import patch

    import questionary

    from utility_belt.dev.janitor import DiscoveredCache
    from utility_belt.ui import dev_menu

    active_cache = DiscoveredCache(Path("dummy/active"), "active", 1024, 100.0, True)
    inactive_cache = DiscoveredCache(Path("dummy/inactive"), "inactive", 2048, 5000000.0, False)

    captured_prompt = {}

    def fake_prompt(factory, text, **kwargs):
        if factory == questionary.text:
            return "."
        if factory == questionary.checkbox:
            captured_prompt["text"] = text
            captured_prompt["choices"] = kwargs.get("choices", [])
            return []  # Cancela fluxo após inspecionar escolhas
        return False

    with patch("utility_belt.ui.dev_menu.scan_caches", return_value=[active_cache, inactive_cache]), \
         patch("utility_belt.ui.dev_menu.prompt", side_effect=fake_prompt):
        dev_menu.run_janitor_flow()

    choices = captured_prompt.get("choices", [])
    assert len(choices) == 2
    assert all(getattr(c, "checked", False) is True for c in choices)
    assert captured_prompt.get("text") == (
        "Selecione as pastas para exclusão ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"
    )


def test_dev_menu_checklist_prompts_have_standard_legend():
    """Prompts de checklist no dev_menu exibem a legenda padronizada ([Espaço] ... [a] ... [Enter] ...)."""
    from unittest.mock import patch

    import questionary

    from utility_belt.dev.git_tidy import LocalBranchInfo, RemoteBranchInfo
    from utility_belt.ui import dev_menu

    expected_legend = "([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"

    # 1. Git-Tidy Local
    captured_local = {}
    local_branch = LocalBranchInfo(name="feat/local", is_current=False, is_protected=False, is_merged=True, is_gone=False)

    def fake_local_prompt(factory, text, **kwargs):
        if factory == questionary.checkbox:
            captured_local["text"] = text
            return []
        return False

    with patch("utility_belt.ui.dev_menu._check_git_environment", return_value=True), \
         patch("utility_belt.ui.dev_menu.prune_remote"), \
         patch("utility_belt.ui.dev_menu.get_local_branches", return_value=[local_branch]), \
         patch("utility_belt.ui.dev_menu.prompt", side_effect=fake_local_prompt):
        dev_menu.run_git_tidy_local_flow()

    assert expected_legend in captured_local.get("text", "")
    assert captured_local.get("text") == (
        f"Selecione as branches locais para remoção {expected_legend}"
    )

    # 2. Git-Tidy Remoto
    captured_remote = {}
    remote_branch = RemoteBranchInfo(name="origin/feat/remote", full_ref="refs/remotes/origin/feat/remote", is_protected=False, is_merged=True)

    def fake_remote_prompt(factory, text, **kwargs):
        if factory == questionary.checkbox:
            captured_remote["text"] = text
            return []
        return False

    with patch("utility_belt.ui.dev_menu._check_git_environment", return_value=True), \
         patch("utility_belt.ui.dev_menu.prune_remote"), \
         patch("utility_belt.ui.dev_menu.get_remote_branches", return_value=[remote_branch]), \
         patch("utility_belt.ui.dev_menu.prompt", side_effect=fake_remote_prompt):
        dev_menu.run_git_tidy_remote_flow()

    assert expected_legend in captured_remote.get("text", "")
    assert captured_remote.get("text") == (
        f"Selecione as branches remotas a excluir no origin {expected_legend}"
    )


def test_run_janitor_flow_deletes_active_cache_by_default_selection():
    """Janitor exclui cache ativo com confirmação de Enter por estar pré-selecionado por padrão."""
    from unittest.mock import patch

    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    from utility_belt.dev.janitor import DiscoveredCache
    from utility_belt.ui import dev_menu

    active_cache = DiscoveredCache(Path("dummy/active_cache"), "active_cache", 4096, 10.0, True)
    with patch("utility_belt.ui.dev_menu.scan_caches", return_value=[active_cache]), \
         patch("utility_belt.ui.dev_menu.delete_cache", return_value=(True, "")) as mock_del:
        with create_pipe_input() as inp:
            inp.send_text("\r\ry")
            with create_app_session(input=inp, output=DummyOutput()):
                dev_menu.run_janitor_flow()
        mock_del.assert_called_once_with(active_cache.path)
