"""Menu interativo principal do Utility Belt com navegação por telas estilo MS-DOS (questionary)."""

from __future__ import annotations

import sys

import questionary
import typer

from utility_belt import __version__
from utility_belt.config import is_banner_enabled
from utility_belt.doctor import run_diagnostics
from utility_belt.ui.screen import (
    clear_screen,
    menu_footer,
    menu_options,
    menu_separator,
    message,
    prompt,
    render_banner,
    render_compact_banner,
    render_header,
    run_dedicated_screen,
    tool_choice,
)


def show_menu() -> None:
    """Exibe o menu principal interativo do Utility Belt com telas dedicadas."""
    if not sys.stdin.isatty():
        print("Erro: O comando 'belt menu' requer um terminal interativo (TTY).", file=sys.stderr)
        sys.exit(2)

    while True:
        clear_screen()
        if is_banner_enabled():
            render_banner()
        else:
            render_compact_banner()
        typer.echo()

        try:
            escolha = prompt(questionary.select,
                "Escolha uma ferramenta",
                choices=[
                    tool_choice(1, "Restic", "Backup, restauração e integridade", "restic"),
                    tool_choice(2, "Docker", "Exportar e importar imagens", "docker"),
                    tool_choice(3, "Markdown", "Converter arquivos, URLs e pastas", "markdown"),
                    tool_choice(4, "Sistema", "Diagnóstico e informações do computador", "system"),
                    menu_separator(),
                    questionary.Choice("[0] Sair", value="sair"),
                    menu_footer(),
                ],
                **menu_options(),
            )
        except KeyboardInterrupt:
            clear_screen()
            typer.echo("Encerrando menu.")
            break

        if escolha is None or escolha == "sair":
            clear_screen()
            typer.echo("Até logo!")
            break

        if escolha == "restic":
            from utility_belt.ui.guard import ensure_dependency

            if not ensure_dependency("restic"):
                continue

            try:
                from utility_belt.ui.restic_menu import show_restic_menu

                show_restic_menu()
            except ImportError:
                run_dedicated_screen("Restic", lambda: message("ERRO", "Módulo do menu Restic não disponível."))

        elif escolha == "docker":
            from utility_belt.ui.guard import ensure_dependency

            if not ensure_dependency("docker"):
                continue

            try:
                from utility_belt.ui.docker_menu import show_docker_menu

                show_docker_menu()
            except ImportError:
                run_dedicated_screen("Docker", lambda: message("ERRO", "Módulo do menu Docker não disponível."))

        elif escolha == "markdown":
            from utility_belt.ui.markdown_menu import show_markdown_menu

            show_markdown_menu()

        elif escolha == "system":
            show_system_menu()


def show_system_menu() -> None:
    actions = {"doctor": ("Verificar ambiente", _show_diagnostics),
               "sysinfo": ("Informações do computador", _run_system_info),
               "about": ("Sobre o Utility Belt", _show_about)}
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "Sistema"])
        typer.echo()
        try:
            choice = prompt(questionary.select, "Escolha uma opção", choices=[
                questionary.Choice("[1] Verificar ambiente", value="doctor"),
                questionary.Choice("[2] Informações do computador", value="sysinfo"),
                questionary.Choice("[3] Sobre o Utility Belt", value="about"),
                menu_separator(),
                questionary.Choice("[0] Voltar ao menu principal", value="exit"),
                menu_footer(),
            ], **menu_options())
        except KeyboardInterrupt:
            return
        if not choice or choice == "exit":
            return
        label, action = actions[choice]
        run_dedicated_screen(["UTILITY BELT", "Sistema", label], action)


def _show_about() -> None:
    message("INFO", f"Utility Belt — versão {__version__}",
            details="O Canivete Suíço de Terminal\nFerramentas para Windows e Linux.\n"
                    "Para atualizar sua instalação: uv tool upgrade utility-belt")


def _show_diagnostics() -> None:
    """Exibe o diagnóstico rápido do ambiente."""
    diag = run_diagnostics()
    typer.echo()
    message("INFO", "Diagnóstico do ambiente.")
    typer.echo(f"  SO       : {diag['system']['os_name']} ({diag['system']['architecture']})")
    typer.echo(f"  Python   : {diag['python']['version']}")

    for name, info in diag["dependencies"].items():
        if info.get("installed"):
            tag = "[OK]"
            details = info.get("details") or info.get("path") or "Disponível"
        else:
            tag = "[FALTA]"
            details = info.get("details") or "Não encontrado no PATH"
        typer.echo(f"  {tag} {name:<12} : {details}")
        if not info.get("installed") and info.get("install_guide"):
            typer.echo(f"       Dica        : {info['install_guide']}")


def _run_system_info() -> None:
    """Executa a ferramenta system.info se disponível no catálogo."""
    from utility_belt.catalog import catalog
    from utility_belt.runner import run_tool

    tool = catalog.get_tool("system.info")
    if tool:
        typer.echo()
        run_tool(tool, args=[])
        typer.echo()
    else:
        typer.secho("Ferramenta 'system.info' não encontrada no catálogo.", fg=typer.colors.YELLOW)
