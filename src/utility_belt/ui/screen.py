"""Módulo de interface de tela e identidade visual retrô estilo MS-DOS do Utility Belt."""

from __future__ import annotations

import os
import shutil
import sys
from typing import Any, Callable

import typer


def ensure_utf8_encoding() -> None:
    """Garante que sys.stdout esteja reconfigurado para UTF-8 quando suportado."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


# Reconfigura na importação do módulo para terminais Windows
ensure_utf8_encoding()

# Códigos de cores ANSI para estética retrô
ORANGE = "\033[38;5;208m"
AMBER = "\033[38;5;214m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
RED = "\033[1;31m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"


def clear_screen() -> None:
    """Limpa a tela do terminal de forma segura e multiplataforma."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        try:
            sys.stdout.write("\033[H\033[2J\033[3J")
            sys.stdout.flush()
        except Exception:
            pass


def get_terminal_width(fallback: int = 80) -> int:
    """Obtém a largura atual do terminal com fallback defensivo."""
    try:
        columns = shutil.get_terminal_size(fallback=(fallback, 24)).columns
        return columns if columns > 0 else fallback
    except Exception:
        return fallback


def render_banner(compact: bool = False) -> None:
    """Renderiza o banner de abertura com arte híbrida (canivete + tipografia 3D)."""
    ensure_utf8_encoding()
    width = get_terminal_width()

    # Se largura for muito estreita ou solicitado modo compacto, exibe banner de 1 linha
    if compact or width < 78:
        render_compact_banner()
        return

    knife_lines = [
        r"      /|     _      ",
        r"     / |    / \     ",
        r"    |  |   /   \    ",
        r"    |  |  /  /\ \   ",
        r"   /   |_/  /  \ \  ",
        r"  |   [+]  /____\ | ",
        r"  |  CANIVETE     | ",
        r"  |  SUÍÇO        | ",
        r"  |_______________| ",
        r"  \_______________/ ",
    ]

    title_lines = [
        (f"{ORANGE}{BOLD}█ █ ▀█▀ ▀█▀ █   ▀█▀ ▀█▀ █ █{RESET}", 27),
        (f"{ORANGE}{BOLD}█ █  █   █  █    █   █  ▀█▀{RESET}", 27),
        (f"{ORANGE}{BOLD}▀▄▀  ▀   ▀  ▀▀▀ ▀▀▀  ▀   ▀{RESET}", 26),
        ("", 0),
        (f"{AMBER}{BOLD}█▀▄ █▀▀ █   ▀█▀{RESET}", 15),
        (f"{AMBER}{BOLD}█▀▄ █▀▀ █    █{RESET}", 14),
        (f"{AMBER}{BOLD}▀▀  ▀▀▀ ▀▀▀  ▀{RESET}", 14),
        (f"{WHITE}v0.1.0 • O Canivete Suíço de Terminal{RESET}", 37),
        (f"{GRAY}Sistema de Ferramentas para Desenvolvedores{RESET}", 43),
        ("", 0),
    ]

    box_w = 76
    inner_w = box_w - 2  # 74

    try:
        typer.echo(f"{CYAN}╔{'═' * inner_w}╗{RESET}")
        for i in range(len(knife_lines)):
            k_raw = knife_lines[i]
            # Colorização do canivete: corpo vermelho com cruz branca, lâminas em branco brilhante
            if i < 5:
                k_colored = f"{WHITE}{k_raw}{RESET}"
            elif i == 5:
                k_colored = f"{RED}  |   {WHITE}[+]{RED}  /____\\ | {RESET}"
            elif i in (6, 7, 8):
                k_colored = f"{RED}{k_raw}{RESET}"
            else:
                k_colored = f"{RED}{k_raw}{RESET}"

            t_colored, t_vis_len = title_lines[i]
            padding_len = 47 - t_vis_len
            t_padded = t_colored + (" " * max(0, padding_len))

            typer.echo(f"{CYAN}║{RESET}  {k_colored} {CYAN}│{RESET}  {t_padded} {CYAN}║{RESET}")

        typer.echo(f"{CYAN}╚{'═' * inner_w}╝{RESET}")
    except (UnicodeEncodeError, Exception):
        # Fallback de máxima compatibilidade ASCII puro se o terminal falhar com UTF-8/cores
        render_ascii_fallback_banner()


def render_compact_banner() -> None:
    """Renderiza um cabeçalho compacto para telas estreitas ou modo minimalista."""
    width = min(get_terminal_width(), 76)
    inner_w = max(10, width - 2)
    title = " [+] UTILITY BELT v0.1.0 — Canivete Suíço de Terminal "
    padded_title = title.center(inner_w)
    typer.echo(f"{CYAN}╔{'═' * inner_w}╗{RESET}")
    typer.echo(f"{CYAN}║{WHITE}{BOLD}{padded_title}{RESET}{CYAN}║{RESET}")
    typer.echo(f"{CYAN}╚{'═' * inner_w}╝{RESET}")


def render_ascii_fallback_banner() -> None:
    """Fallback simples em caso de falha de codificação."""
    print("+--------------------------------------------------------------------------+")
    print("| [+] UTILITY BELT v0.1.0 -- O Canivete Suico de Terminal                  |")
    print("+--------------------------------------------------------------------------+")


def render_header(breadcrumbs: list[str] | str) -> None:
    """Renderiza uma barra de navegação/breadcrumbs em moldura retrô estilo MS-DOS."""
    ensure_utf8_encoding()
    if isinstance(breadcrumbs, str):
        trail = breadcrumbs
    else:
        trail = " > ".join(b.strip() for b in breadcrumbs if b.strip())

    box_w = min(get_terminal_width(), 76)
    inner_w = max(10, box_w - 2)

    label = f" {trail} "
    if len(label) > inner_w:
        label = label[: inner_w - 3] + "... "

    padding = inner_w - len(label)
    try:
        typer.echo(f"{CYAN}╔{'═' * inner_w}╗{RESET}")
        typer.echo(f"{CYAN}║{WHITE}{BOLD}{label}{RESET}{' ' * max(0, padding)}{CYAN}║{RESET}")
        typer.echo(f"{CYAN}╚{'═' * inner_w}╝{RESET}")
    except Exception:
        print(f"=== {trail} ===")


def run_dedicated_screen(
    title: str | list[str],
    func: Callable[..., Any],
    *args: Any,
    wait_for_key: bool = True,
    **kwargs: Any,
) -> Any:
    """Executa uma ação em tela dedicada com limpeza prévia, cabeçalho e confirmação de retorno."""
    clear_screen()
    breadcrumbs = [title] if isinstance(title, str) else list(title)
    render_header(breadcrumbs)
    typer.echo()

    try:
        result = func(*args, **kwargs)
    except Exception as e:
        typer.secho(f"\nErro durante a execução: {e}", fg=typer.colors.RED)
        result = None

    if wait_for_key and sys.stdin.isatty():
        typer.echo()
        try:
            import questionary

            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar ao menu...").ask()
        except (KeyboardInterrupt, EOFError, Exception):
            pass

    clear_screen()
    return result
