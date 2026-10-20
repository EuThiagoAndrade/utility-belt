"""Cinco ações Markdown nas telas existentes do Utility Belt."""

from __future__ import annotations

import sys

import questionary
import typer

from utility_belt import markdown as core
from utility_belt.adapters.markdown import progress, report
from utility_belt.config import load_markdown_output_dir, save_markdown_output_dir
from utility_belt.markdown_watch import watch
from utility_belt.ui.screen import (
    clear_screen,
    menu_footer,
    menu_options,
    menu_separator,
    message,
    prompt,
    render_header,
    run_dedicated_screen,
)


def configure_output() -> bool:
    value = prompt(questionary.path, "Pasta central de saída (vazio cancela):", only_directories=True)
    if not value:
        message("CANCELADO", "Operação cancelada.")
        return False
    output = save_markdown_output_dir(value)
    message("SUCESSO", "Pasta de saída configurada.", details=f"Destino: {output}")
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
            source = prompt(questionary.text, "Arquivo ou URL HTTP(S) (vazio cancela):")
        elif choice in ("batch", "watch"):
            source = prompt(questionary.path, "Pasta de entrada (vazio cancela):", only_directories=True)
        if choice != "clipboard" and not source:
            message("CANCELADO", "Operação cancelada.")
            return
        labels = {"convert": "Preparando a conversão do arquivo ou URL...",
                  "batch": "Preparando a conversão da pasta...", "watch": "Preparando o monitor...",
                  "clipboard": "Lendo o caminho ou URL da área de transferência..."}
        message("INFO", labels[choice])
        if choice == "watch":
            result = watch(source, on_result=progress,
                           on_ready=lambda: message("INFO", "Monitor ativo. Ctrl+C para encerrar e voltar."))
        elif choice == "batch":
            result = core.batch(source, on_result=progress)
        elif choice == "clipboard":
            result = core.clipboard()
        else:
            result = core.convert(source)
        report(result)
    except KeyboardInterrupt:
        message("CANCELADO", "Operação cancelada.")
    except (OSError, ValueError) as err:
        message("ERRO", "Não foi possível concluir a operação.", details=str(err))


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
    )]
    choices.append(menu_separator())
    choices.append(questionary.Choice("[0] Voltar ao menu principal", "exit"))
    choices.append(menu_footer())
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "MARKDOWN"])
        try:
            choice = prompt(questionary.select, "Markdown — Escolha uma opção:", choices=choices,
                                        **menu_options())
            if not choice or choice == "exit":
                return
            titles = {"convert": "Converter arquivo ou URL", "batch": "Converter pasta",
                      "watch": "Monitorar novos arquivos", "clipboard": "Área de transferência",
                      "config": "Configurar pasta de saída"}
            run_dedicated_screen(["UTILITY BELT", "Markdown", titles[choice]], execute, choice)
        except KeyboardInterrupt:
            return
