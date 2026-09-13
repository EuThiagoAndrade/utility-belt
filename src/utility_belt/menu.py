"""Menu interativo principal do Utility Belt com navegação por setas (questionary)."""

from __future__ import annotations

import sys

import questionary
import typer

from utility_belt.doctor import run_diagnostics


def show_menu() -> None:
    """Exibe o menu principal interativo do Utility Belt com questionary."""
    if not sys.stdin.isatty():
        print("Erro: O comando 'belt menu' requer um terminal interativo (TTY).", file=sys.stderr)
        sys.exit(2)

    while True:
        typer.echo()
        typer.secho("  UTILITY BELT - CANIVETE SUÍÇO", bold=True)
        typer.echo()

        try:
            escolha = questionary.select(
                "Escolha uma opção:",
                choices=[
                    questionary.Choice("🛡️  Restic (Backups, Restauração e Integridade)", value="restic"),
                    questionary.Choice("🐳  Docker (Exportar e Importar Imagens)", value="docker"),
                    questionary.Choice("🩺  Diagnóstico e Saúde (Doctor)", value="doctor"),
                    questionary.Choice("ℹ️   Informações do Sistema (system.info)", value="sysinfo"),
                    questionary.Separator(),
                    questionary.Choice("🚪  Sair", value="sair"),
                ],
                use_shortcuts=False,
                instruction="(Use ↑↓ para navegar, Enter para selecionar)",
            ).ask()
        except KeyboardInterrupt:
            typer.echo("\nEncerrando menu.")
            break

        if escolha is None or escolha == "sair":
            typer.echo("Até logo!")
            break

        if escolha == "restic":
            try:
                from utility_belt.ui.restic_menu import show_restic_menu

                show_restic_menu()
            except ImportError:
                typer.secho("Módulo do menu Restic não disponível.", fg=typer.colors.RED, err=True)

        elif escolha == "docker":
            try:
                from utility_belt.ui.docker_menu import show_docker_menu

                show_docker_menu()
            except ImportError:
                typer.secho("Módulo do menu Docker não disponível.", fg=typer.colors.RED, err=True)

        elif escolha == "doctor":
            _show_diagnostics()

        elif escolha == "sysinfo":
            _run_system_info()


def _show_diagnostics() -> None:
    """Exibe o diagnóstico rápido do ambiente."""
    diag = run_diagnostics()
    typer.echo()
    typer.secho("=== Diagnóstico Rápido ===", bold=True)
    typer.echo(f"  SO       : {diag['system']['os_name']} ({diag['system']['architecture']})")
    typer.echo(f"  Python   : {diag['python']['version']}")

    for name, info in diag["dependencies"].items():
        if info.get("installed"):
            tag = typer.style("[OK]", fg=typer.colors.GREEN, bold=True)
            details = info.get("details") or info.get("path") or "Disponível"
        else:
            tag = typer.style("[FALTA]", fg=typer.colors.YELLOW)
            details = info.get("details") or "Não encontrado no PATH"
        typer.echo(f"  {tag} {name:<12} : {details}")

    typer.echo()
    try:
        questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
    except (KeyboardInterrupt, EOFError):
        pass


def _run_system_info() -> None:
    """Executa a ferramenta system.info se disponível no catálogo."""
    from utility_belt.catalog import catalog
    from utility_belt.runner import run_tool

    tool = catalog.get_tool("system.info")
    if tool:
        typer.echo()
        run_tool(tool, args=[])
        typer.echo()
        try:
            questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
        except (KeyboardInterrupt, EOFError):
            pass
    else:
        typer.secho("Ferramenta 'system.info' não encontrada no catálogo.", fg=typer.colors.YELLOW)
