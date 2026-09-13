"""Adaptador Typer para subcomandos Restic."""

from __future__ import annotations

from pathlib import Path

import typer

from utility_belt.catalog import catalog
from utility_belt.runner import run_tool

restic_app = typer.Typer(
    name="restic",
    help="Comandos para backup, restauração e integridade com Restic.",
    no_args_is_help=True,
)


def _exec_restic_tool(subcommand: str, extra_args: list[str], non_interactive: bool = False) -> None:
    tool = catalog.get_tool("restic.backup")
    if not tool:
        typer.secho("Erro: Ferramenta 'restic.backup' não encontrada no catálogo.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    full_args = [subcommand] + extra_args
    exit_code = run_tool(tool, args=full_args, non_interactive=non_interactive)
    raise typer.Exit(code=exit_code)


@restic_app.command(name="backup", help="Executa backup incremental com Restic.")
def restic_backup(
    repo: str | None = typer.Option(None, "--repo", "-r", help="Caminho do repositório."),
    source: str | None = typer.Option(None, "--source", "-s", help="Pasta de origem a salvar."),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Nome do perfil de configuração."),
    exclude_file: Path | None = typer.Option(None, "--exclude-file", help="Arquivo com padrões de exclusão."),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Proíbe prompts interativos de senha."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simula o backup."),
) -> None:
    args: list[str] = []
    if repo:
        args.extend(["--repo", repo])
    if source:
        args.extend(["--source", source])
    if profile:
        args.extend(["--profile", profile])
    if exclude_file:
        args.extend(["--exclude-file", str(exclude_file)])
    if non_interactive:
        args.append("--non-interactive")
    if dry_run:
        args.append("--dry-run")

    _exec_restic_tool("backup", args, non_interactive=non_interactive)


@restic_app.command(name="restore", help="Restaura arquivos de um snapshot Restic.")
def restic_restore(
    snapshot: str = typer.Option("latest", "--snapshot", help="ID do snapshot ou 'latest'."),
    target: Path | None = typer.Option(None, "--target", "-t", help="Pasta onde restaurar os arquivos."),
    repo: str | None = typer.Option(None, "--repo", "-r", help="Caminho do repositório."),
    include: str | None = typer.Option(None, "--include", help="Filtro opcional para restaurar apenas arquivos específicos."),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Nome do perfil de configuração."),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Proíbe prompts interativos."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simula a restauração."),
) -> None:
    args: list[str] = ["--snapshot", snapshot]
    if target:
        args.extend(["--target", str(target)])
    if repo:
        args.extend(["--repo", repo])
    if include:
        args.extend(["--include", include])
    if profile:
        args.extend(["--profile", profile])
    if non_interactive:
        args.append("--non-interactive")
    if dry_run:
        args.append("--dry-run")

    _exec_restic_tool("restore", args, non_interactive=non_interactive)


@restic_app.command(name="check", help="Verifica a integridade e referências do repositório.")
def restic_check(
    repo: str | None = typer.Option(None, "--repo", "-r", help="Caminho do repositório."),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Nome do perfil de configuração."),
    read_data: bool = typer.Option(False, "--read-data", help="Lê todos os dados dos arquivos para conferência total."),
) -> None:
    args: list[str] = []
    if repo:
        args.extend(["--repo", repo])
    if profile:
        args.extend(["--profile", profile])
    if read_data:
        args.append("--read-data")

    _exec_restic_tool("check", args)


@restic_app.command(name="snapshots", help="Lista todos os snapshots existentes no repositório.")
def restic_snapshots(
    repo: str | None = typer.Option(None, "--repo", "-r", help="Caminho do repositório."),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Nome do perfil de configuração."),
) -> None:
    args: list[str] = []
    if repo:
        args.extend(["--repo", repo])
    if profile:
        args.extend(["--profile", profile])

    _exec_restic_tool("snapshots", args)


@restic_app.command(name="init", help="Inicializa deliberadamente um novo repositório Restic.")
def restic_init(
    repo: str = typer.Option(..., "--repo", "-r", help="Caminho do novo repositório."),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Nome do perfil onde salvar o ID gerado."),
) -> None:
    args = ["--repo", repo]
    if profile:
        args.extend(["--profile", profile])

    _exec_restic_tool("init", args)


@restic_app.command(name="migrate-config", help="Migra a configuração do ResticMenu para o config.toml do Utility Belt.")
def restic_migrate_config() -> None:
    _exec_restic_tool("migrate-config", [])
