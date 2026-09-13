"""Adaptador Typer para subcomandos Docker."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from utility_belt.catalog import catalog
from utility_belt.runner import run_tool

docker_app = typer.Typer(
    name="docker",
    help="Comandos para exportação e importação segura de imagens Docker.",
    no_args_is_help=False,
)


@docker_app.callback(invoke_without_command=True)
def docker_callback(ctx: typer.Context) -> None:
    """Abre o menu interativo do Docker quando chamado sem subcomando."""
    if ctx.invoked_subcommand is None:
        if sys.stdin.isatty():
            from utility_belt.ui.docker_menu import show_docker_menu

            show_docker_menu()
        else:
            typer.echo(ctx.get_help())
            raise typer.Exit()


@docker_app.command(name="export", help="Exporta imagens Docker para arquivo .tar com manifesto.")
def export_images(
    image: list[str] | None = typer.Option(
        None, "--image", "-i", help="Nome e tag da imagem (ex.: alpine:latest). Pode ser repetido."
    ),
    all_images: bool = typer.Option(
        False, "--all", "-a", help="Exporta todas as imagens disponíveis localmente."
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Caminho do arquivo .tar ou pasta de saída."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simula a exportação sem gerar o arquivo."
    ),
) -> None:
    tool = catalog.get_tool("docker.export")
    if not tool:
        typer.secho("Erro: Ferramenta 'docker.export' não encontrada no catálogo.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    args: list[str] = []
    if image:
        for img in image:
            args.extend(["--image", img])
    if all_images:
        args.append("--all")
    if output:
        args.extend(["--output", str(output)])
    if dry_run:
        args.append("--dry-run")

    exit_code = run_tool(tool, args=args)
    raise typer.Exit(code=exit_code)


@docker_app.command(name="import", help="Importa imagens Docker a partir de um arquivo .tar.")
def import_images(
    input_file: Path | None = typer.Option(
        None, "--input", "-i", help="Caminho do arquivo .tar para importação."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Valida arquivo e exibe manifesto sem carregar no Docker."
    ),
    run_container: bool = typer.Option(
        False, "--run", help="Oferece iniciar um container interativamente após importar."
    ),
) -> None:
    tool = catalog.get_tool("docker.import")
    if not tool:
        typer.secho("Erro: Ferramenta 'docker.import' não encontrada no catálogo.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    args: list[str] = []
    if input_file:
        args.extend(["--input", str(input_file)])
    if dry_run:
        args.append("--dry-run")
    if run_container:
        args.append("--run")

    exit_code = run_tool(tool, args=args)
    raise typer.Exit(code=exit_code)


@docker_app.command(name="menu", help="Abre o menu interativo do Docker.")
def docker_menu_cmd() -> None:
    import sys

    if not sys.stdin.isatty():
        typer.secho("Erro: 'belt docker menu' requer um terminal interativo (TTY).", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    from utility_belt.ui.docker_menu import show_docker_menu

    show_docker_menu()
