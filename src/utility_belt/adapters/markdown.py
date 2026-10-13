"""Interface Typer compartilhada pela CLI e pela entrada do catálogo."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from utility_belt import markdown as core
from utility_belt.config import save_markdown_output_dir
from utility_belt.markdown_watch import watch
from utility_belt.ui.screen import message

markdown_app = typer.Typer(name="markdown", help="Conversão Markdown de arquivos, URLs e pastas.",
                           no_args_is_help=False, add_completion=False)


def report(result: core.ConversionResult | core.OperationResult) -> None:
    """Mostra diagnósticos e destinos sem alterar o conteúdo do motor."""
    kind = "CANCELADO" if result.code == 130 else "SUCESSO" if result.code == 0 else "AVISO" if result.code == 2 else "ERRO"
    if isinstance(result, core.OperationResult):
        title = "Operação encerrada." if result.code == 130 else "Conversão em lote concluída."
        if result.code != 130 and result.failures and result.successes:
            kind, title = "AVISO", "Conversão concluída com pendências."
        message(kind, title)
        typer.echo(f"Convertidos: {result.successes} | Com erro: {result.failures} | Ignorados: {result.ignored}")
    else:
        titles = {"success": "Arquivo convertido para Markdown.", "partial": "Conversão parcial; verifique os detalhes.",
                  "cancelled": "Operação cancelada.", "unsupported": "Formato não suportado.",
                  "unavailable": "Um requisito está indisponível.", "missing": "Um requisito está ausente.",
                  "changed": "Arquivo alterado durante a conversão; tente novamente.", "failed": "Não foi possível converter."}
        if result.status == "partial":
            kind = "AVISO"
        message(kind, titles.get(result.status, "Operação concluída." if result.code == 0 else "Operação não concluída."))
        if result.output:
            typer.echo(f"Salvo em: {result.output}")
    if result.diagnostic:
        typer.echo(f"Detalhes: {result.diagnostic}")
    if result.operation:
        typer.echo(f"Pasta da operação: {result.operation}")


def progress(path: Path, result: core.ConversionResult) -> None:
    typer.echo(f"\nArquivo: {path}")
    report(result)


def announce(text: str) -> None:
    if sys.stdin.isatty() and sys.stdout.isatty():
        message("INFO", text)


def automation(ctx: typer.Context, requested: bool) -> bool:
    return requested or bool(ctx.obj and ctx.obj.get("non_interactive"))


@markdown_app.callback(invoke_without_command=True)
def callback(ctx: typer.Context, non_interactive: bool = typer.Option(False, "--non-interactive")) -> None:
    ctx.obj = {"non_interactive": non_interactive}
    if ctx.invoked_subcommand is None:
        if sys.stdin.isatty() and not non_interactive:
            from utility_belt.ui.markdown_menu import show_markdown_menu
            show_markdown_menu()
        else:
            typer.echo(ctx.get_help())


@markdown_app.command("convert", help="Converte um arquivo ou URL HTTP(S).")
def convert(ctx: typer.Context, source: str = typer.Argument(...),
            output_dir: Path | None = typer.Option(None, "--output-dir"),
            non_interactive: bool = typer.Option(False, "--non-interactive")) -> None:
    announce("Preparando a conversão do arquivo ou URL...")
    result = core.convert(source, output_dir=output_dir, non_interactive=automation(ctx, non_interactive))
    report(result)
    raise typer.Exit(result.code)


@markdown_app.command("batch", help="Converte uma pasta recursivamente, em lote sequencial.")
def batch(ctx: typer.Context, source: Path = typer.Argument(...),
          output_dir: Path | None = typer.Option(None, "--output-dir"),
          non_interactive: bool = typer.Option(False, "--non-interactive")) -> None:
    announce("Preparando a conversão da pasta...")
    result = core.batch(source, output_dir=output_dir, non_interactive=automation(ctx, non_interactive),
                        on_result=progress)
    report(result)
    raise typer.Exit(result.code)


@markdown_app.command("watch", help="Monitora novos arquivos em primeiro plano; Ctrl+C encerra.")
def monitor(ctx: typer.Context, source: Path = typer.Argument(...),
            output_dir: Path | None = typer.Option(None, "--output-dir"),
            non_interactive: bool = typer.Option(False, "--non-interactive")) -> None:
    announce("Preparando o monitor...")
    result = watch(source, output_dir=output_dir, non_interactive=automation(ctx, non_interactive),
                   on_result=progress, on_ready=lambda: typer.echo("Monitor ativo; Ctrl+C para encerrar."))
    report(result)
    raise typer.Exit(result.code)


@markdown_app.command("clipboard", help="Converte o arquivo ou URL textual do clipboard.")
def clipboard(ctx: typer.Context, output_dir: Path | None = typer.Option(None, "--output-dir"),
              non_interactive: bool = typer.Option(False, "--non-interactive")) -> None:
    announce("Lendo o caminho ou URL da área de transferência...")
    result = core.clipboard(output_dir=output_dir, non_interactive=automation(ctx, non_interactive))
    report(result)
    raise typer.Exit(result.code)


@markdown_app.command("config", help="Persiste a pasta central sem substituir perfis existentes.")
def configure(output_dir: Path = typer.Option(..., "--output-dir")) -> None:
    try:
        output = save_markdown_output_dir(output_dir)
    except KeyboardInterrupt:
        typer.echo("Configuração cancelada.")
        raise typer.Exit(130) from None
    except (OSError, ValueError) as err:
        typer.echo(f"Configuração inválida: {err}", err=True)
        raise typer.Exit(2) from None
    typer.echo(f"Destino Markdown configurado: {output}")


@markdown_app.command("menu", help="Abre o submenu Markdown em terminal interativo.")
def menu(ctx: typer.Context, non_interactive: bool = typer.Option(False, "--non-interactive")) -> None:
    if not sys.stdin.isatty() or automation(ctx, non_interactive):
        typer.echo("O menu Markdown requer um terminal interativo (TTY).", err=True)
        raise typer.Exit(2)
    from utility_belt.ui.markdown_menu import show_markdown_menu
    show_markdown_menu()
