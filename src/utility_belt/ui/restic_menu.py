"""Menu interativo do Restic com navegação por setas (questionary)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

import questionary
import typer

from utility_belt.config import get_profile, load_config, set_profile
from utility_belt.restic_diagnostics import (
    diagnose_restic_result,
    format_menu_guidance,
)
from utility_belt.ui.screen import (
    clear_screen,
    menu_footer,
    menu_options,
    menu_separator,
    prompt,
    render_header,
    run_dedicated_screen,
    status_message,
)

# Global password for the session
_session_password: str | None = None


def get_restic_env() -> dict[str, str]:
    """Retorna as variáveis de ambiente necessárias para o restic."""
    env = os.environ.copy()
    if _session_password:
        env["RESTIC_PASSWORD"] = _session_password
    return env


def ask_password_if_needed() -> bool:
    """Solicita a senha do restic se ainda não estiver configurada. Retorna False se cancelado."""
    global _session_password
    if _session_password:
        return True

    if "RESTIC_PASSWORD" in os.environ:
        _session_password = os.environ["RESTIC_PASSWORD"]
        return True

    try:
        password = prompt(questionary.password, "Digite a senha do repositório Restic:")
        if not password:
            return False
        _session_password = password
        return True
    except KeyboardInterrupt:
        return False


def _extract_subcommand(cmd_args: list[str]) -> str:
    known_subs = {"backup", "restore", "check", "snapshots", "unlock", "init", "ls"}
    for arg in cmd_args:
        if arg in known_subs:
            return arg
    return "restic"


def _extract_repo_from_args(cmd_args: list[str]) -> str | None:
    for i, arg in enumerate(cmd_args):
        if arg == "-r" and i + 1 < len(cmd_args):
            return cmd_args[i + 1]
        elif arg.startswith("-r="):
            return arg.split("=", 1)[1]
        elif arg.startswith("--repo="):
            return arg.split("=", 1)[1]
        elif arg == "--repo" and i + 1 < len(cmd_args):
            return cmd_args[i + 1]
    return None


def _execute_restic(
    cmd_args: list[str],
    capture_output: bool = False,
) -> subprocess.CompletedProcess[Any] | None:
    try:
        if capture_output:
            return subprocess.run(
                ["restic"] + cmd_args,
                env=get_restic_env(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        else:
            res = subprocess.run(
                ["restic"] + cmd_args,
                env=get_restic_env(),
                stdout=None,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if res.stderr and isinstance(res.stderr, str):
                sys.stderr.write(res.stderr)
                sys.stderr.flush()
            return res
    except FileNotFoundError:
        status_message(
            "Executável 'restic' não encontrado. Certifique-se de que está instalado e no PATH.",
            fg=typer.colors.RED,
        )
        return None
    except KeyboardInterrupt:
        status_message("\nOperação cancelada pelo usuário.", fg=typer.colors.YELLOW)
        return None


def run_restic(
    cmd_args: list[str],
    capture_output: bool = False,
    allow_lock_recovery: bool = True,
) -> subprocess.CompletedProcess[Any] | None:
    """Executa um comando restic de forma segura, com streaming e diagnóstico assistido."""
    if not ask_password_if_needed():
        return None

    res = _execute_restic(cmd_args, capture_output=capture_output)
    if res is None:
        return None

    subcmd = _extract_subcommand(cmd_args)

    # Se a operação terminou com código 11 (falha de lock) e a recuperação assistida é cabível
    if res.returncode == 11 and allow_lock_recovery and subcmd != "unlock":
        diag = diagnose_restic_result(subcmd, 11, res.stderr or "", getattr(res, "stdout", "") or "")
        if diag:
            status_message("\n" + format_menu_guidance(diag), fg=typer.colors.YELLOW)

        while True:
            choice = prompt(
                questionary.select,
                "Falha de lock no repositório (código 11). Como deseja prosseguir?",
                choices=[
                    questionary.Choice("Aguardar e tentar novamente (limite de 1 minuto)", "retry"),
                    questionary.Choice("Executar unlock (desbloquear locks obsoletos)", "unlock"),
                    questionary.Choice("Voltar", "back"),
                ],
            )
            if choice == "retry":
                status_message("\nTentando novamente com espera de até 1 minuto (--retry-lock 1m)...", fg=typer.colors.CYAN)
                retry_args = list(cmd_args)
                if "--retry-lock" not in retry_args:
                    retry_args.extend(["--retry-lock", "1m"])
                retry_res = _execute_restic(retry_args, capture_output=capture_output)
                if retry_res is not None and retry_res.returncode == 0:
                    return retry_res
                elif retry_res is not None and retry_res.returncode == 11:
                    diag = diagnose_restic_result(subcmd, 11, retry_res.stderr or "", getattr(retry_res, "stdout", "") or "")
                    if diag:
                        status_message("\n" + format_menu_guidance(diag), fg=typer.colors.YELLOW)
                    continue
                else:
                    return retry_res
            elif choice == "unlock":
                repo = _extract_repo_from_args(cmd_args)
                if not repo:
                    status_message("Não foi possível identificar o repositório nos argumentos.", fg=typer.colors.RED)
                    return res

                status_message(
                    "\nAviso: Remova locks apenas se nenhuma outra operação estiver em execução no repositório.",
                    fg=typer.colors.YELLOW,
                )
                confirmed = prompt(
                    questionary.confirm,
                    "Tem certeza de que deseja executar 'restic unlock' para remover locks obsoletos?",
                    default=False,
                )
                if confirmed:
                    status_message("\nExecutando 'restic unlock'...", fg=typer.colors.CYAN)
                    unlock_res = _execute_restic(["-r", repo, "unlock"], capture_output=False)
                    if unlock_res is not None and unlock_res.returncode == 0:
                        status_message("\nLocks obsoletos removidos com sucesso.", fg=typer.colors.GREEN)
                    else:
                        status_message("\nFalha ao executar unlock.", fg=typer.colors.RED)
                else:
                    status_message("Desbloqueio cancelado pelo usuário.", fg=typer.colors.YELLOW)
                # Preserva o código 11 da operação original sem repetição automática
                return res
            else:  # "back" ou None
                return res

    # Se unlock falhar com código 11, exibe diagnóstico sem oferecer unlock recursivo
    if res.returncode == 11 and subcmd == "unlock":
        diag = diagnose_restic_result("unlock", 11, res.stderr or "")
        if diag:
            status_message("\n" + format_menu_guidance(diag), fg=typer.colors.YELLOW)
        return res

    return res


def show_wizard() -> None:
    """Assistente passo-a-passo para novos usuários."""
    status_message("\n=== Assistente de Configuração Restic ===", fg=typer.colors.CYAN)

    config = load_config()
    profile = get_profile()
    restic_config = profile.get("restic", {})

    repo = prompt(questionary.path, "Caminho do repositório (destino):", default=restic_config.get("repo", ""))
    if repo is None:
        return

    source = prompt(questionary.path, "Caminho de origem (backup):", default=restic_config.get("source", ""))
    if source is None:
        return

    restore_parent = prompt(questionary.path, "Caminho padrão para restauração:", default=restic_config.get("restore_parent", ""))
    if restore_parent is None:
        return

    exclude_file = prompt(questionary.path, "Arquivo de exclusão (opcional):", default=restic_config.get("exclude_file", ""))
    if exclude_file is None:
        return

    global _session_password
    password = prompt(questionary.password, "Senha do repositório:")
    if password:
        _session_password = password

    restic_config.update({
        "repo": repo,
        "source": source,
        "restore_parent": restore_parent,
        "exclude_file": exclude_file
    })

    profile["restic"] = restic_config
    default_profile_name = config.get("default_profile", "padrao")
    set_profile(default_profile_name, profile)

    status_message("Configuração salva com sucesso!", fg=typer.colors.GREEN)

    if prompt(questionary.confirm, "Deseja inicializar o repositório agora?"):
        status_message("Inicializando repositório...", fg=typer.colors.CYAN)
        run_restic(["-r", repo, "init"])


def do_backup() -> None:
    """Executa o backup."""
    profile = get_profile()
    restic_config = profile.get("restic", {})
    repo = restic_config.get("repo")
    source = restic_config.get("source")

    if not repo or not source:
        status_message("Configuração incompleta. Configure o repositório e a origem primeiro.", fg=typer.colors.RED)
        return

    dry_run = prompt(questionary.confirm, "Deseja executar como simulação (dry-run)?", default=False)
    if dry_run is None:
        return

    cmd = ["-r", repo, "backup", source]
    if dry_run:
        cmd.append("--dry-run")

    exclude_file = restic_config.get("exclude_file")
    if exclude_file and os.path.exists(exclude_file):
        cmd.extend(["--exclude-file", exclude_file])

    status_message(f"\nIniciando backup de {source} para {repo}...", fg=typer.colors.CYAN)
    res = run_restic(cmd)
    if res is not None:
        if res.returncode == 0:
            status_message("\nBackup concluído com sucesso!", fg=typer.colors.GREEN)
        elif res.returncode == 3:
            diag = diagnose_restic_result("backup", 3, res.stderr or "")
            if diag:
                status_message("\n" + format_menu_guidance(diag), fg=typer.colors.YELLOW)
        elif res.returncode != 11:
            diag = diagnose_restic_result("backup", res.returncode, res.stderr or "")
            if diag:
                status_message("\n" + format_menu_guidance(diag), fg=typer.colors.RED)


def get_snapshots() -> list[dict[str, Any]]:
    """Obtém a lista de snapshots no formato JSON."""
    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    if not repo:
        status_message("Repositório não configurado.", fg=typer.colors.RED)
        return []

    result = run_restic(["-r", repo, "snapshots", "--json"], capture_output=True)
    if result and result.stdout:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    return []


def do_restore() -> None:
    """Restauração guiada de snapshots."""
    snapshots = get_snapshots()
    if not snapshots:
        status_message("Nenhum snapshot encontrado ou erro ao carregar snapshots.", fg=typer.colors.YELLOW)
        return

    choices = []
    for snap in snapshots:
        short_id = snap["id"][:8]
        time_str = snap["time"][:19].replace("T", " ")
        paths_str = ", ".join(snap.get("paths", []))
        label = f"[{short_id}] {time_str} - {paths_str}"
        choices.append(questionary.Choice(title=label, value=snap["id"]))

    snap_id = prompt(questionary.select,
        "Selecione o snapshot para restaurar:",
        choices=choices
    )

    if not snap_id:
        return

    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    default_restore = profile.get("restic", {}).get("restore_parent", "")

    target = prompt(questionary.path, "Diretório de destino para restauração:", default=default_restore)
    if not target:
        return

    include_filter = prompt(questionary.text, "Filtro de arquivos (opcional, ex: *.txt):")
    if include_filter is None:
        return

    cmd = ["-r", repo, "restore", snap_id, "--target", target]
    if include_filter:
        cmd.extend(["--include", include_filter])

    status_message(f"\nIniciando restauração para {target}...", fg=typer.colors.CYAN)
    result = run_restic(cmd)

    if result is not None and result.returncode == 0:
        status_message("\nRestauração concluída com sucesso!", fg=typer.colors.GREEN)
        if prompt(questionary.confirm, "Deseja abrir a pasta no Windows Explorer?"):
            os.startfile(target)
    elif result is not None and result.returncode != 0:
        if result.returncode != 11:
            diag = diagnose_restic_result("restore", result.returncode, result.stderr or "")
            if diag:
                status_message("\n" + format_menu_guidance(diag), fg=typer.colors.RED)


def do_check() -> None:
    """Verificação estrutural e de dados do repositório."""
    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    if not repo:
        status_message("Repositório não configurado.", fg=typer.colors.RED)
        return

    mode = prompt(questionary.select,
        "Selecione o modo de verificação:",
        choices=[
            questionary.Choice("Verificação rápida (apenas estrutura)", "quick"),
            questionary.Choice("Verificação completa (--read-data)", "full")
        ]
    )

    if not mode:
        return

    cmd = ["-r", repo, "check"]
    if mode == "full":
        cmd.append("--read-data")

    status_message(f"\nIniciando verificação ({mode})...", fg=typer.colors.CYAN)
    res = run_restic(cmd)
    if res is not None:
        if res.returncode == 0:
            status_message("\nVerificação concluída com sucesso! Repositório íntegro.", fg=typer.colors.GREEN)
        elif res.returncode != 11:
            diag = diagnose_restic_result("check", res.returncode, res.stderr or "")
            if diag:
                status_message("\n" + format_menu_guidance(diag), fg=typer.colors.RED)


def do_unlock() -> None:
    """Executa o desbloqueio de locks obsoletos com confirmação explícita."""
    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    if not repo:
        status_message("Repositório não configurado.", fg=typer.colors.RED)
        return

    status_message(f"Repositório: {repo}", fg=typer.colors.CYAN)
    status_message(
        "Aviso: Execute o desbloqueio apenas se tiver certeza de que nenhuma outra operação está em andamento.",
        fg=typer.colors.YELLOW,
    )
    confirmed = prompt(questionary.confirm, "Deseja realmente executar o desbloqueio (unlock)?", default=False)
    if not confirmed:
        status_message("Operação cancelada pelo usuário.", fg=typer.colors.YELLOW)
        return

    status_message("\nExecutando 'restic unlock'...", fg=typer.colors.CYAN)
    res = run_restic(["-r", repo, "unlock"], allow_lock_recovery=False)
    if res is not None and res.returncode == 0:
        status_message("\nLocks obsoletos removidos com sucesso!", fg=typer.colors.GREEN)
    elif res is not None and res.returncode != 11:
        diag = diagnose_restic_result("unlock", res.returncode, res.stderr or "")
        if diag:
            status_message("\n" + format_menu_guidance(diag), fg=typer.colors.RED)


def do_ls() -> None:
    """Navegação/inspeção de arquivos nos snapshots."""
    snapshots = get_snapshots()
    if not snapshots:
        status_message("Nenhum snapshot encontrado.", fg=typer.colors.YELLOW)
        return

    choices = []
    for snap in snapshots:
        short_id = snap["id"][:8]
        time_str = snap["time"][:19].replace("T", " ")
        paths_str = ", ".join(snap.get("paths", []))
        label = f"[{short_id}] {time_str} - {paths_str}"
        choices.append(questionary.Choice(title=label, value=snap["id"]))

    snap_id = prompt(questionary.select,
        "Selecione o snapshot para listar os arquivos:",
        choices=choices
    )

    if not snap_id:
        return

    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")

    status_message(f"\nListando arquivos do snapshot {snap_id[:8]}...", fg=typer.colors.CYAN)
    run_restic(["-r", repo, "ls", snap_id])


def edit_config() -> None:
    """Edita a configuração de caminhos e exclusões."""
    config = load_config()
    profile = get_profile()
    restic_config = profile.get("restic", {})

    repo = prompt(questionary.path, "Repositório:", default=restic_config.get("repo", ""))
    if repo is None:
        return

    source = prompt(questionary.path, "Origem (backup):", default=restic_config.get("source", ""))
    if source is None:
        return

    restore_parent = prompt(questionary.path, "Pai de restauração:", default=restic_config.get("restore_parent", ""))
    if restore_parent is None:
        return

    exclude_file = prompt(questionary.path, "Arquivo de exclusões:", default=restic_config.get("exclude_file", ""))
    if exclude_file is None:
        return

    restic_config.update({
        "repo": repo,
        "source": source,
        "restore_parent": restore_parent,
        "exclude_file": exclude_file
    })

    profile["restic"] = restic_config
    default_profile_name = config.get("default_profile", "padrao")
    set_profile(default_profile_name, profile)
    status_message("Configuração atualizada com sucesso!", fg=typer.colors.GREEN)


def show_restic_menu() -> None:
    """Ponto de entrada principal para o menu interativo Restic."""
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "RESTIC"])
        typer.echo()
        try:
            choice = prompt(questionary.select,
                "Menu Restic — Escolha uma opção:",
                choices=[
                    questionary.Choice("[1] Assistente Inicial (Novo Usuário)", "wizard"),
                    questionary.Choice("[2] Fazer Backup", "backup"),
                    questionary.Choice("[3] Restaurar Snapshot", "restore"),
                    questionary.Choice("[4] Verificar Repositório (check)", "check"),
                    questionary.Choice("[5] Listar Arquivos (ls)", "ls"),
                    questionary.Choice("[6] Desbloquear locks obsoletos (unlock)", "unlock"),
                    questionary.Choice("[7] Configurar Caminhos", "config"),
                    menu_separator(),
                    questionary.Choice("[0] Voltar ao menu principal", "exit"),
                    menu_footer(),
                ],
                **menu_options(),
            )

            if not choice or choice == "exit":
                break

            if choice == "wizard":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "ASSISTENTE"], show_wizard)
            elif choice == "backup":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "BACKUP"], do_backup)
            elif choice == "restore":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "RESTAURAÇÃO"], do_restore)
            elif choice == "check":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "VERIFICAÇÃO"], do_check)
            elif choice == "ls":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "LISTAR ARQUIVOS"], do_ls)
            elif choice == "unlock":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "DESBLOQUEIO"], do_unlock)
            elif choice == "config":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "CONFIGURAÇÃO"], edit_config)

        except KeyboardInterrupt:
            break
        except Exception as e:
            status_message(f"\nOcorreu um erro: {e}", fg=typer.colors.RED)
            break


if __name__ == "__main__":
    show_restic_menu()
