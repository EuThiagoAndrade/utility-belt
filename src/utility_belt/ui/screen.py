"""Apresentação compacta de terminal, compartilhada por menus e resultados."""

from __future__ import annotations

import inspect
import os
import shutil
import sys
import textwrap
from typing import Any, Callable

import questionary
import typer
from prompt_toolkit.styles import Style

from utility_belt import __version__


def ensure_utf8_encoding() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


ensure_utf8_encoding()


def color_enabled() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"


def clear_screen() -> None:
    """Limpa somente um terminal real, na transição entre telas."""
    if not sys.stdout.isatty():
        return
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except OSError:
        typer.echo("\033[H\033[2J", nl=False)


def get_terminal_width(fallback: int = 80) -> int:
    try:
        return max(1, shutil.get_terminal_size(fallback=(fallback, 24)).columns)
    except (OSError, ValueError):
        return fallback


def _line(text: str, *, fg: str | None = None, bold: bool = False) -> None:
    width = min(get_terminal_width(), 96)
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width=width, replace_whitespace=False) or [""]:
            typer.secho(line, fg=fg, bold=bold, color=color_enabled())


def _rule() -> None:
    _line("─" * min(get_terminal_width(), 96), fg=typer.colors.CYAN)


def render_banner(compact: bool = False) -> None:
    """Cabeçalho principal com cinto textual e versão canônica."""
    if compact:
        render_compact_banner()
        return
    width = min(get_terminal_width(), 96)
    title, version = "[==[]==]  UTILITY BELT", f"v{__version__}"
    if width >= len(title) + len(version) + 2:
        typer.secho("[==[]==]  ", fg=typer.colors.YELLOW, nl=False, color=color_enabled())
        _line("UTILITY BELT" + " " * (width - len(title) - len(version)) + version,
              fg=typer.colors.CYAN, bold=True)
    else:
        _line(f"UTILITY BELT  {version}", fg=typer.colors.CYAN, bold=True)
    _line("O Canivete Suíço de Terminal", fg=typer.colors.BRIGHT_BLACK)
    _rule()
    _line("Início", fg=typer.colors.CYAN)


def render_compact_banner() -> None:
    _line(f"UTILITY BELT  v{__version__}", fg=typer.colors.CYAN, bold=True)
    _rule()
    _line("Início", fg=typer.colors.CYAN)


def render_ascii_fallback_banner() -> None:
    _line(f"[==[]==] UTILITY BELT v{__version__}")
    _line("O Canivete Suico de Terminal")
    _line("-" * min(get_terminal_width(), 96))


def render_header(breadcrumbs: list[str] | str) -> None:
    _line(f"UTILITY BELT  v{__version__}", fg=typer.colors.CYAN, bold=True)
    _rule()
    parts = [breadcrumbs] if isinstance(breadcrumbs, str) else breadcrumbs
    trail = " > ".join(part.strip() for part in parts if part.strip() and part != "UTILITY BELT")
    _line(trail, fg=typer.colors.CYAN)


def menu_style() -> Style:
    if not color_enabled():
        return Style.from_dict({key: "" for key in (
            "qmark", "question", "answer", "pointer", "highlighted", "selected", "instruction", "description", "separator", "text",
        )})
    return Style.from_dict({
        "qmark": "", "question": "bold #e6edf3", "answer": "#51d4e8",
        "pointer": "bold bg:#123239 #51d4e8", "highlighted": "bold bg:#123239 #51d4e8",
        "selected": "#51d4e8", "instruction": "#9299a5", "description": "#9299a5", "separator": "#9299a5",
    })


def menu_options() -> dict[str, Any]:
    return {"qmark": "", "pointer": ">", "style": menu_style(),
            "instruction": " "}


def menu_separator() -> questionary.Separator:
    return questionary.Separator("─" * max(1, min(get_terminal_width(), 96) - 4))


def menu_footer() -> questionary.Separator:
    width = max(1, min(get_terminal_width(), 96) - 4)
    navigation = "\n".join(textwrap.wrap("↑↓ Navegar · Enter Selecionar · Ctrl+C Voltar/Sair", width=width))
    return questionary.Separator("\n" + "─" * width + "\n" + navigation)


def tool_choice(number: int, label: str, description: str, value: str) -> questionary.Choice:
    width = min(get_terminal_width(), 96)
    label_lines = textwrap.wrap(f"[{number}] {label}", width=max(1, width - 3))
    title = "\n".join(line.ljust(max(1, width - 3)) for line in label_lines)
    detail = "\n".join(("    " + line).ljust(width) for line in textwrap.wrap(description, width=max(1, width - 4)))
    return questionary.Choice(f"{title}\n{detail}\n", value=value)


def message(kind: str, text: str, *, details: str | None = None) -> None:
    """Começa um bloco novo mesmo após um subprocesso sem newline final."""
    colors = {"SUCESSO": typer.colors.GREEN, "AVISO": typer.colors.YELLOW,
              "ERRO": typer.colors.RED, "INFO": typer.colors.CYAN,
              "CANCELADO": typer.colors.BRIGHT_BLACK}
    typer.echo()
    _line(f"[{kind}] {text}", fg=colors.get(kind), bold=True)
    if details:
        _line(details)
    typer.echo()


def status_message(text: str, *, fg: str | None = None, bold: bool = False) -> None:
    """Adapta mensagens dos assistentes existentes ao mesmo formato."""
    if "cancelad" in text.lower():
        kind = "CANCELADO"
    else:
        kind = {typer.colors.RED: "ERRO", typer.colors.YELLOW: "AVISO",
                typer.colors.GREEN: "SUCESSO"}.get(fg, "INFO")
    message(kind, text.strip())


def prompt(factory: Callable[..., Any], text: str, **kwargs: Any) -> Any:
    """Toda pergunta começa em linha própria, após saída de ferramentas."""
    typer.echo()
    kwargs.setdefault("style", menu_style())
    if "use_shortcuts" in kwargs:
        try:
            params = inspect.signature(factory).parameters
            if "use_shortcuts" not in params:
                kwargs.pop("use_shortcuts")
        except (TypeError, ValueError):
            pass
    return factory(text, **kwargs).ask()


def run_dedicated_screen(
    title: str | list[str], func: Callable[..., Any], *args: Any,
    wait_for_key: bool = True, **kwargs: Any,
) -> Any:
    """Preserva perguntas e resultado na tela até confirmação de retorno."""
    clear_screen()
    render_header([title] if isinstance(title, str) else list(title))
    typer.echo()
    try:
        result = func(*args, **kwargs)
    except KeyboardInterrupt:
        message("CANCELADO", "Operação cancelada pelo usuário.")
        result = None
    except Exception as exc:
        message("ERRO", "Não foi possível concluir a operação.", details=str(exc))
        result = None
    if wait_for_key and sys.stdin.isatty():
        typer.echo()
        try:
            questionary.press_any_key_to_continue(
                "Pressione qualquer tecla para voltar ao menu...", style=menu_style(),
            ).ask()
        except (KeyboardInterrupt, EOFError):
            pass
    # A tela receptora limpa ao renderizar; nunca apagar um resultado sem espera.
    return result
