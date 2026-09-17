"""Testes unitários para o módulo de telas e banner retrô (utility_belt.ui.screen)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from utility_belt.config import get_default_config, is_banner_enabled
from utility_belt.ui.screen import (
    clear_screen,
    get_terminal_width,
    render_ascii_fallback_banner,
    render_banner,
    render_compact_banner,
    render_header,
    run_dedicated_screen,
)


def test_clear_screen_calls_os_system() -> None:
    """Verifica se clear_screen executa o comando de limpeza de tela."""
    with patch("os.system") as mock_system:
        clear_screen()
        mock_system.assert_called_once()


def test_clear_screen_catches_exceptions() -> None:
    """Garante que clear_screen não propaga exceções caso o os.system falhe."""
    with patch("os.system", side_effect=RuntimeError("Terminal não suportado")):
        # Não deve levantar exceção
        clear_screen()


def test_get_terminal_width_default() -> None:
    """Testa obtenção de largura com fallback seguro."""
    width = get_terminal_width(fallback=80)
    assert isinstance(width, int)
    assert width > 0


def test_get_terminal_width_on_exception() -> None:
    """Testa retorno do fallback quando get_terminal_size falha."""
    with patch("shutil.get_terminal_size", side_effect=OSError("Sem TTY")):
        assert get_terminal_width(fallback=85) == 85


def test_render_banner_standard(capsys) -> None:
    """Testa renderização do banner completo em terminal padrão."""
    with patch("utility_belt.ui.screen.get_terminal_width", return_value=80):
        render_banner(compact=False)
        captured = capsys.readouterr()
        assert "╔" in captured.out
        assert "CANIVETE" in captured.out
        assert "SUÍÇO" in captured.out
        assert "v0.1.0" in captured.out


def test_render_banner_auto_compact_on_narrow_terminal(capsys) -> None:
    """Testa ativação automática de banner compacto em terminal menor que 78 colunas."""
    with patch("utility_belt.ui.screen.get_terminal_width", return_value=60):
        render_banner(compact=False)
        captured = capsys.readouterr()
        assert "UTILITY BELT" in captured.out
        # No modo compacto não deve exibir os blocos grandes
        assert "CANIVETE" not in captured.out


def test_render_banner_explicit_compact(capsys) -> None:
    """Testa renderização compacta explícita."""
    with patch("utility_belt.ui.screen.get_terminal_width", return_value=100):
        render_banner(compact=True)
        captured = capsys.readouterr()
        assert "UTILITY BELT" in captured.out
        assert "CANIVETE" not in captured.out


def test_render_compact_banner_structure(capsys) -> None:
    """Testa estrutura do cabeçalho compacto."""
    with patch("utility_belt.ui.screen.get_terminal_width", return_value=80):
        render_compact_banner()
        captured = capsys.readouterr()
        assert "╔" in captured.out
        assert "UTILITY BELT" in captured.out
        assert "╚" in captured.out


def test_render_ascii_fallback_banner(capsys) -> None:
    """Testa banner de fallback puramente ASCII."""
    render_ascii_fallback_banner()
    captured = capsys.readouterr()
    assert "+--------------------------------------------------------------------------+" in captured.out
    assert "UTILITY BELT" in captured.out


def test_render_header_with_list(capsys) -> None:
    """Testa cabeçalho com lista de breadcrumbs."""
    with patch("utility_belt.ui.screen.get_terminal_width", return_value=80):
        render_header(["UTILITY BELT", "DOCKER", "EXPORTAR"])
        captured = capsys.readouterr()
        assert "UTILITY BELT > DOCKER > EXPORTAR" in captured.out


def test_render_header_with_string(capsys) -> None:
    """Testa cabeçalho com string única."""
    with patch("utility_belt.ui.screen.get_terminal_width", return_value=80):
        render_header("DIAGNÓSTICO DO SISTEMA")
        captured = capsys.readouterr()
        assert "DIAGNÓSTICO DO SISTEMA" in captured.out


def test_run_dedicated_screen_executes_and_returns() -> None:
    """Testa execução de função dentro do wrapper de tela dedicada."""
    mock_action = MagicMock(return_value="resultado_ok")

    with patch("utility_belt.ui.screen.clear_screen") as mock_clear, \
         patch("utility_belt.ui.screen.render_header") as mock_header:
        res = run_dedicated_screen(
            title="TESTE",
            func=mock_action,
            arg1="val1",
            wait_for_key=False,
            custom_kw="kw1"
        )
        assert res == "resultado_ok"
        mock_action.assert_called_once_with(arg1="val1", custom_kw="kw1")
        assert mock_clear.call_count == 2
        mock_header.assert_called_once_with(["TESTE"])


def test_run_dedicated_screen_handles_exception(capsys) -> None:
    """Testa comportamento quando a função executada lança erro."""
    def failing_func():
        raise ValueError("Falha simulada na ação")

    with patch("utility_belt.ui.screen.clear_screen"):
        res = run_dedicated_screen("TESTE FALHA", failing_func, wait_for_key=False)
        assert res is None
        captured = capsys.readouterr()
        assert "Erro durante a execução: Falha simulada na ação" in captured.out


def test_is_banner_enabled_default(tmp_path) -> None:
    """Testa se is_banner_enabled retorna True por padrão."""
    with patch("utility_belt.config.get_config_dir", return_value=tmp_path):
        assert is_banner_enabled() is True
        default_cfg = get_default_config()
        assert default_cfg.get("show_banner") is True


def test_is_banner_enabled_when_disabled(tmp_path) -> None:
    """Testa se is_banner_enabled respeita valor False na configuração."""
    cfg = {"show_banner": False}
    with patch("utility_belt.config.load_config", return_value=cfg):
        assert is_banner_enabled() is False
