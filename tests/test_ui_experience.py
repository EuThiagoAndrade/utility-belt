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
