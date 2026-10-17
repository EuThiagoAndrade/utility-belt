"""Adaptador CLI para ferramentas de desenvolvimento (Janitor e Git-Tidy)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from utility_belt.dev.git_tidy import (
    delete_local_branches,
    delete_remote_branches,
    get_local_branches,
    get_remote_branches,
    is_git_installed,
    is_inside_git_repo,
    prune_remote,
)
from utility_belt.dev.janitor import delete_cache, format_size, scan_caches
from utility_belt.ui.screen import message

dev_app = typer.Typer(
    name="dev",
    help="Ferramentas de desenvolvimento: Faxineiro de Caches (Janitor) e Git-Tidy.",
    no_args_is_help=False,
    add_completion=False,
)


@dev_app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        if sys.stdin.isatty():
            from utility_belt.ui.dev_menu import show_dev_menu

            show_dev_menu()
        else:
            typer.echo(ctx.get_help())


@dev_app.command("janitor", help="Detecta e limpa pastas de dependências e caches de build.")
def janitor(
    path: Path = typer.Argument(Path("."), help="Diretório raiz da varredura."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Apenas simula a exclusão."),
    days: int = typer.Option(30, "--days", "-d", help="Dias para considerar projeto ativo."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma exclusão sem confirmação interativa."),
) -> None:
    resolved = path.resolve()
    if not resolved.is_dir():
        typer.echo(f"Erro: '{path}' não é um diretório válido.", err=True)
        raise typer.Exit(2)

    caches = scan_caches(resolved, days_threshold=days)
    if not caches:
        message("SUCESSO", "Nenhum diretório de cache descartável encontrado.")
        raise typer.Exit(0)

    total_bytes = sum(c.size_bytes for c in caches)
    typer.echo(f"Pastas de cache identificadas em '{resolved}':")
    for c in caches:
        active_tag = "[ATIVO]" if c.is_active else "[INATIVO]"
        typer.echo(f"  {active_tag} {c.target_name} ({c.formatted_size}) — {c.formatted_time_ago}")
        typer.echo(f"    {c.path}")

    typer.echo(f"\nTotal: {len(caches)} pasta(s) encontradas ({format_size(total_bytes)}).")

    if dry_run:
        message("INFO", "Modo simulação (--dry-run): nenhum arquivo ou diretório foi excluído.")
        raise typer.Exit(0)

    # Se não passou --yes e está em terminal interativo, solicita confirmação
    if not yes:
        if sys.stdin.isatty():
            confirmed = typer.confirm("Deseja prosseguir com a exclusão definitiva?")
            if not confirmed:
                message("CANCELADO", "Operação cancelada pelo usuário.")
                raise typer.Exit(0)
        else:
            typer.echo("Aviso: Use --yes ou --dry-run em ambientes não interativos.", err=True)
            raise typer.Exit(2)

    success_count = 0
    fail_count = 0
    freed = 0
    for c in caches:
        ok, err = delete_cache(c.path, dry_run=False)
        if ok:
            success_count += 1
            freed += c.size_bytes
        else:
            fail_count += 1
            typer.echo(f"  [ERRO] Falha ao excluir {c.path}: {err}", err=True)

    if fail_count == 0:
        message(
            "SUCESSO",
            f"{success_count} pasta(s) excluída(s) com sucesso!",
            details=f"Espaço liberado: {format_size(freed)}",
        )
    else:
        message(
            "AVISO",
            f"Concluído com falhas: {success_count} excluída(s), {fail_count} erro(s).",
            details=f"Espaço liberado: {format_size(freed)}",
        )
        raise typer.Exit(1)


@dev_app.command("git-tidy", help="Higieniza branches locais e remotas mescladas ou órfãs.")
def git_tidy(
    dry_run: bool = typer.Option(False, "--dry-run", help="Apenas simula a exclusão."),
    remote: bool = typer.Option(False, "--remote", help="Higieniza branches remotas em origin."),
    all_targets: bool = typer.Option(False, "--all", help="Higieniza branches locais e remotas."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma exclusão sem confirmação interativa."),
) -> None:
    if not is_git_installed():
        typer.echo("Erro: Git não está instalado ou acessível no PATH.", err=True)
        raise typer.Exit(2)

    if not is_inside_git_repo():
        typer.echo("Erro: Diretório atual não é um repositório Git.", err=True)
        raise typer.Exit(2)

    # Sincronização preventiva
    prune_remote()

    do_local = not remote or all_targets
    do_remote = remote or all_targets

    # 1. Higienização Local
    if do_local:
        local_branches = get_local_branches()
        eligible_local = [b for b in local_branches if b.is_eligible_for_deletion]

        if not eligible_local:
            typer.echo("Nenhuma branch local órfã ou mergeada para exclusão.")
        else:
            typer.echo(f"Branches locais elegíveis para remoção ({len(eligible_local)}):")
            for b in eligible_local:
                typer.echo(f"  {b.name} {b.status_label}")

            if dry_run:
                typer.echo("  [SIMULAÇÃO] git branch -D " + " ".join(b.name for b in eligible_local))
            else:
                confirmed = yes
                if not confirmed and sys.stdin.isatty():
                    confirmed = typer.confirm(f"Excluir as {len(eligible_local)} branches locais?")
                elif not confirmed:
                    typer.echo("Aviso: Use --yes ou --dry-run em ambientes não interativos.", err=True)
                    raise typer.Exit(2)

                if confirmed:
                    results = delete_local_branches([b.name for b in eligible_local], dry_run=False)
                    for name, (ok, err) in results.items():
                        if ok:
                            typer.echo(f"  [OK] Removida localmente: {name}")
                        else:
                            typer.echo(f"  [ERRO] {name}: {err}", err=True)

    # 2. Higienização Remota
    if do_remote:
        remote_branches = get_remote_branches()
        eligible_remote = [b for b in remote_branches if b.is_eligible_for_deletion]

        if not eligible_remote:
            typer.echo("Nenhuma branch remota mergeada encontrada em origin.")
        else:
            typer.echo(f"\nBranches remotas em origin elegíveis para remoção ({len(eligible_remote)}):")
            for b in eligible_remote:
                typer.echo(f"  {b.full_ref} {b.status_label}")

            if dry_run:
                typer.echo("  [SIMULAÇÃO] git push origin --delete " + " ".join(b.name for b in eligible_remote))
            else:
                confirmed = yes
                if not confirmed and sys.stdin.isatty():
                    confirmed = typer.confirm(
                        f"ATENÇÃO: Excluir definitivamente {len(eligible_remote)} branches no origin?"
                    )
                elif not confirmed:
                    typer.echo("Aviso: Use --yes ou --dry-run em ambientes não interativos.", err=True)
                    raise typer.Exit(2)

                if confirmed:
                    results = delete_remote_branches([b.name for b in eligible_remote], dry_run=False)
                    for name, (ok, err) in results.items():
                        if ok:
                            typer.echo(f"  [OK] Removida no origin: {name}")
                        else:
                            typer.echo(f"  [ERRO] {name}: {err}", err=True)


@dev_app.command("menu", help="Abre o menu interativo de Desenvolvimento em TTY.")
def menu() -> None:
    if not sys.stdin.isatty():
        typer.echo("Erro: O comando 'belt dev menu' requer um terminal interativo (TTY).", err=True)
        raise typer.Exit(2)
    from utility_belt.ui.dev_menu import show_dev_menu

    show_dev_menu()
