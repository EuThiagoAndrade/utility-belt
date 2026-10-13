"""Cinco ações Markdown nas telas existentes do Utility Belt."""

from __future__ import annotations

import sys

import questionary
import typer

from utility_belt import markdown as core
from utility_belt.adapters.markdown import progress, report
from utility_belt.config import load_markdown_output_dir, save_markdown_output_dir
from utility_belt.markdown_watch import watch
from utility_belt.ui.screen import clear_screen, render_header, run_dedicated_screen


def configure_output() -> bool:
    value = questionary.path("Pasta central de saída (vazio cancela):", only_directories=True).ask()
    if not value:
        typer.echo("Operação cancelada.")
        return False
    output = save_markdown_output_dir(value)
    typer.echo(f"Destino Markdown configurado: {output}")
    return True


def execute(choice: str) -> None:
    try:
        if choice == "config":
            configure_output()
            return
        if load_markdown_output_dir() is None and not configure_output():
            return
        source = None
        if choice == "convert":
            source = questionary.text("Arquivo ou URL HTTP(S) (vazio cancela):").ask()
        elif choice in ("batch", "watch"):
            source = questionary.path("Pasta de entrada (vazio cancela):", only_directories=True).ask()
        if choice != "clipboard" and not source:
            typer.echo("Operação cancelada.")
            return
        if choice == "watch":
            result = watch(source, on_result=progress,
                           on_ready=lambda: typer.echo("Monitor ativo; Ctrl+C para voltar."))
        elif choice == "batch":
            result = core.batch(source, on_result=progress)
        elif choice == "clipboard":
            result = core.clipboard()
        else:
            result = core.convert(source)
        report(result)
    except KeyboardInterrupt:
        typer.echo("Operação cancelada.")
    except (OSError, ValueError) as err:
        typer.echo(f"Erro: {err}", err=True)


def show_markdown_menu() -> None:
    if not sys.stdin.isatty():
        typer.echo("O menu Markdown requer um terminal interativo (TTY).", err=True)
        return
    choices = [questionary.Choice(label, value=value) for label, value in (
        ("[1] Converter arquivo ou URL", "convert"),
        ("[2] Converter pasta em lote", "batch"),
        ("[3] Monitorar novos arquivos", "watch"),
        ("[4] Converter caminho ou URL do clipboard", "clipboard"),
        ("[5] Configurar pasta central", "config"),
        ("[0] Voltar ao menu principal", "exit"),
    )]
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "MARKDOWN"])
        try:
            choice = questionary.select("Markdown — Escolha uma opção:", choices=choices,
                                        use_shortcuts=False,
                                        instruction="(Use ↑↓ para navegar, Enter para selecionar)").ask()
            if not choice or choice == "exit":
                return
            run_dedicated_screen(["UTILITY BELT", "MARKDOWN", choice.upper()], execute, choice)
        except KeyboardInterrupt:
            return
