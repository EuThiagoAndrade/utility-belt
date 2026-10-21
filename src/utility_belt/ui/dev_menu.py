"""Submenu interativo MS-DOS para ferramentas de desenvolvimento (Janitor e Git-Tidy)."""

from __future__ import annotations

import sys
from pathlib import Path

import questionary
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


def run_janitor_flow() -> None:
    """Fluxo interativo do Janitor para varredura e limpeza de caches."""
    target_str = prompt(
        questionary.text,
        "Diretório para varredura de caches (vazio usa o diretório atual):",
        default=".",
    )
    if not target_str:
        message("CANCELADO", "Operação cancelada.")
        return

    target_path = Path(target_str).resolve()
    if not target_path.is_dir():
        message("ERRO", f"O caminho '{target_str}' não é um diretório válido.")
        return

    message("INFO", f"Analisando caches descartáveis em: {target_path} ...")
    caches = scan_caches(target_path)

    if not caches:
        message("SUCESSO", "Nenhum diretório de cache descartável encontrado na pasta analisada.")
        return

    choices = [
        questionary.Choice(
            f"{c.target_name} ({c.formatted_size}) — {c.formatted_time_ago}\n    {c.path}",
            value=c,
            checked=True,
        )
        for c in caches
    ]

    typer.echo()
    selected_caches: list = prompt(
        questionary.checkbox,
        "Selecione as pastas para exclusão ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):",
        choices=choices,
        **menu_options(),
    )

    if not selected_caches:
        message("INFO", "Nenhuma pasta selecionada. Nenhuma alteração realizada.")
        return

    total_bytes = sum(c.size_bytes for c in selected_caches)
    confirmed = prompt(
        questionary.confirm,
        f"Confirma a exclusão permanente de {len(selected_caches)} pasta(s) ({format_size(total_bytes)})?",
        default=False,
    )

    if not confirmed:
        message("CANCELADO", "Exclusão cancelada pelo usuário.")
        return

    success_count = 0
    fail_count = 0
    freed_bytes = 0

    for c in selected_caches:
        ok, err = delete_cache(c.path)
        if ok:
            success_count += 1
            freed_bytes += c.size_bytes
        else:
            fail_count += 1
            typer.echo(f"  [ERRO] Falha ao excluir {c.path}: {err}", err=True)

    if fail_count == 0:
        message(
            "SUCESSO",
            f"{success_count} pasta(s) excluída(s) com sucesso!",
            details=f"Espaço total liberado no disco: {format_size(freed_bytes)}",
        )
    else:
        message(
            "AVISO",
            f"Limpeza concluída com pendências: {success_count} excluída(s), {fail_count} falha(s).",
            details=f"Espaço liberado: {format_size(freed_bytes)}",
        )


def _check_git_environment() -> bool:
    """Valida se o ambiente é adequado para operações do Git-Tidy."""
    if not is_git_installed():
        message("ERRO", "Git não encontrado no PATH do sistema operacional.")
        return False
    if not is_inside_git_repo():
        message("ERRO", "O diretório atual não está dentro de um repositório Git válido.")
        return False
    return True


def run_git_tidy_local_flow() -> None:
    """Fluxo interativo de limpeza de branches locais."""
    if not _check_git_environment():
        return

    message("INFO", "Sincronizando referências locais com o remoto (git fetch --prune)...")
    prune_remote()

    branches = get_local_branches()
    eligible = [b for b in branches if b.is_eligible_for_deletion]

    if not eligible:
        message("SUCESSO", "Nenhuma branch local órfã ou mergeada para limpeza.")
        return

    choices = [
        questionary.Choice(
            f"{b.name} {b.status_label}",
            value=b.name,
            checked=True,
        )
        for b in eligible
    ]

    selected_names: list[str] = prompt(
        questionary.checkbox,
        "Selecione as branches locais para remoção ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):",
        choices=choices,
        **menu_options(),
    )

    if not selected_names:
        message("INFO", "Nenhuma branch selecionada.")
        return

    confirmed = prompt(
        questionary.confirm,
        f"Excluir localmente as {len(selected_names)} branch(es) selecionada(s)?",
        default=False,
    )

    if not confirmed:
        message("CANCELADO", "Operação cancelada.")
        return

    results = delete_local_branches(selected_names)
    successes = sum(1 for ok, _ in results.values() if ok)
    failures = len(results) - successes

    if failures == 0:
        message("SUCESSO", f"{successes} branch(es) local(is) removida(s) com sucesso.")
    else:
        message("AVISO", f"Operação concluída com {failures} erro(s).")
        for name, (ok, err) in results.items():
            if not ok:
                typer.echo(f"  {name}: {err}", err=True)


def run_git_tidy_remote_flow() -> None:
    """Fluxo interativo de limpeza de branches remotas em origin."""
    if not _check_git_environment():
        return

    message("INFO", "Sincronizando referências remotas (git fetch --prune)...")
    prune_remote()

    remotes = get_remote_branches()
    eligible = [b for b in remotes if b.is_eligible_for_deletion]

    if not eligible:
        message("SUCESSO", "Nenhuma branch remota mergeada encontrada para exclusão.")
        return

    choices = [
        questionary.Choice(
            f"{b.full_ref} {b.status_label}",
            value=b.name,
            checked=True,
        )
        for b in eligible
    ]

    selected_names: list[str] = prompt(
        questionary.checkbox,
        "Selecione as branches remotas a excluir no origin ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):",
        choices=choices,
        **menu_options(),
    )

    if not selected_names:
        message("INFO", "Nenhuma branch selecionada.")
        return

    message(
        "AVISO",
        "ATENÇÃO: A exclusão de branches remotas afeta o repositório compartilhado no servidor.",
    )
    confirmed = prompt(
        questionary.confirm,
        f"Confirma a exclusão de {len(selected_names)} branch(es) no origin?",
        default=False,
    )

    if not confirmed:
        message("CANCELADO", "Operação remota cancelada.")
        return

    results = delete_remote_branches(selected_names)
    successes = sum(1 for ok, _ in results.values() if ok)
    failures = len(results) - successes

    if failures == 0:
        message("SUCESSO", f"{successes} branch(es) remota(s) removida(s) no origin.")
    else:
        message("AVISO", f"Operação remota concluída com {failures} erro(s).")
        for name, (ok, err) in results.items():
            if not ok:
                typer.echo(f"  {name}: {err}", err=True)


def run_git_tidy_all_flow() -> None:
    """Executa a higienização de branches locais e em seguida remotas."""
    run_git_tidy_local_flow()
    typer.echo()
    run_git_tidy_remote_flow()


def show_dev_menu() -> None:
    """Exibe o menu interativo de Ferramentas de Desenvolvimento."""
    if not sys.stdin.isatty():
        typer.echo("O menu de Desenvolvimento requer um terminal interativo (TTY).", err=True)
        return

    choices = [
        questionary.Choice(label, value=val)
        for label, val in (
            ("[1] Faxineiro de Caches (Janitor)", "janitor"),
            ("[2] Higienizar Branches Locais (Git-Tidy)", "git_local"),
            ("[3] Higienizar Branches Remotas (Git-Tidy)", "git_remote"),
            ("[4] Higienização Completa (Local e Remoto)", "git_all"),
        )
    ]
    choices.append(menu_separator())
    choices.append(questionary.Choice("[0] Voltar ao menu principal", value="exit"))
    choices.append(menu_footer())

    while True:
        clear_screen()
        render_header(["UTILITY BELT", "DESENVOLVIMENTO"])
        try:
            choice = prompt(
                questionary.select,
                "Desenvolvimento — Escolha uma ferramenta:",
                choices=choices,
                **menu_options(),
            )
            if not choice or choice == "exit":
                return

            screens = {
                "janitor": ("Faxineiro de Caches (Janitor)", run_janitor_flow),
                "git_local": ("Git-Tidy: Branches Locais", run_git_tidy_local_flow),
                "git_remote": ("Git-Tidy: Branches Remotas", run_git_tidy_remote_flow),
                "git_all": ("Git-Tidy: Higienização Completa", run_git_tidy_all_flow),
            }

            title, func = screens[choice]
            run_dedicated_screen(["UTILITY BELT", "Desenvolvimento", title], func)
        except KeyboardInterrupt:
            return
