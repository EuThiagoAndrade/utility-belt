"""Menu interativo do Restic com navegação por setas (questionary)."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

import questionary
import typer

from utility_belt.config import get_profile, load_config, set_profile
from utility_belt.ui.screen import clear_screen, render_header, run_dedicated_screen

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
        password = questionary.password("Digite a senha do repositório Restic:").ask()
        if not password:
            return False
        _session_password = password
        return True
    except KeyboardInterrupt:
        return False


def run_restic(cmd_args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess[Any] | None:
    """Executa um comando restic de forma segura."""
    if not ask_password_if_needed():
        return None

    try:
        if capture_output:
            return subprocess.run(
                ["restic"] + cmd_args,
                env=get_restic_env(),
                capture_output=True,
                text=True,
                check=True
            )
        else:
            return subprocess.run(
                ["restic"] + cmd_args,
                env=get_restic_env(),
                check=True
            )
    except subprocess.CalledProcessError as e:
        typer.secho(f"Erro ao executar restic: {e}", fg=typer.colors.RED)
        if e.stderr:
            typer.secho(e.stderr, fg=typer.colors.RED)
        return None
    except FileNotFoundError:
        typer.secho("Executável 'restic' não encontrado. Certifique-se de que está instalado e no PATH.", fg=typer.colors.RED)
        return None
    except KeyboardInterrupt:
        typer.secho("\nOperação cancelada pelo usuário.", fg=typer.colors.YELLOW)
        return None


def show_wizard() -> None:
    """Assistente passo-a-passo para novos usuários."""
    typer.secho("\n=== Assistente de Configuração Restic ===", fg=typer.colors.CYAN)

    config = load_config()
    profile = get_profile()
    restic_config = profile.get("restic", {})

    repo = questionary.path("Caminho do repositório (destino):", default=restic_config.get("repo", "")).ask()
    if repo is None:
        return

    source = questionary.path("Caminho de origem (backup):", default=restic_config.get("source", "")).ask()
    if source is None:
        return

    restore_parent = questionary.path("Caminho padrão para restauração:", default=restic_config.get("restore_parent", "")).ask()
    if restore_parent is None:
        return

    exclude_file = questionary.path("Arquivo de exclusão (opcional):", default=restic_config.get("exclude_file", "")).ask()
    if exclude_file is None:
        return

    global _session_password
    password = questionary.password("Senha do repositório:").ask()
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

    typer.secho("Configuração salva com sucesso!", fg=typer.colors.GREEN)

    if questionary.confirm("Deseja inicializar o repositório agora?").ask():
        typer.secho("Inicializando repositório...", fg=typer.colors.CYAN)
        run_restic(["-r", repo, "init"])


def do_backup() -> None:
    """Executa o backup."""
    profile = get_profile()
    restic_config = profile.get("restic", {})
    repo = restic_config.get("repo")
    source = restic_config.get("source")

    if not repo or not source:
        typer.secho("Configuração incompleta. Configure o repositório e a origem primeiro.", fg=typer.colors.RED)
        return

    dry_run = questionary.confirm("Deseja executar como simulação (dry-run)?", default=False).ask()
    if dry_run is None:
        return

    cmd = ["-r", repo, "backup", source]
    if dry_run:
        cmd.append("--dry-run")

    exclude_file = restic_config.get("exclude_file")
    if exclude_file and os.path.exists(exclude_file):
        cmd.extend(["--exclude-file", exclude_file])

    typer.secho(f"\nIniciando backup de {source} para {repo}...", fg=typer.colors.CYAN)
    run_restic(cmd)


def get_snapshots() -> list[dict[str, Any]]:
    """Obtém a lista de snapshots no formato JSON."""
    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    if not repo:
        typer.secho("Repositório não configurado.", fg=typer.colors.RED)
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
        typer.secho("Nenhum snapshot encontrado ou erro ao carregar snapshots.", fg=typer.colors.YELLOW)
        return

    choices = []
    for snap in snapshots:
        short_id = snap["id"][:8]
        time_str = snap["time"][:19].replace("T", " ")
        paths_str = ", ".join(snap.get("paths", []))
        label = f"[{short_id}] {time_str} - {paths_str}"
        choices.append(questionary.Choice(title=label, value=snap["id"]))

    snap_id = questionary.select(
        "Selecione o snapshot para restaurar:",
        choices=choices
    ).ask()

    if not snap_id:
        return

    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    default_restore = profile.get("restic", {}).get("restore_parent", "")

    target = questionary.path("Diretório de destino para restauração:", default=default_restore).ask()
    if not target:
        return

    include_filter = questionary.text("Filtro de arquivos (opcional, ex: *.txt):").ask()
    if include_filter is None:
        return

    cmd = ["-r", repo, "restore", snap_id, "--target", target]
    if include_filter:
        cmd.extend(["--include", include_filter])

    typer.secho(f"\nIniciando restauração para {target}...", fg=typer.colors.CYAN)
    result = run_restic(cmd)

    if result is not None:
        if questionary.confirm("Restauração concluída. Deseja abrir a pasta no Windows Explorer?").ask():
            os.startfile(target)


def do_check() -> None:
    """Verificação estrutural e de dados do repositório."""
    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")
    if not repo:
        typer.secho("Repositório não configurado.", fg=typer.colors.RED)
        return

    mode = questionary.select(
        "Selecione o modo de verificação:",
        choices=[
            questionary.Choice("Verificação rápida (apenas estrutura)", "quick"),
            questionary.Choice("Verificação completa (--read-data)", "full")
        ]
    ).ask()

    if not mode:
        return

    cmd = ["-r", repo, "check"]
    if mode == "full":
        cmd.append("--read-data")

    typer.secho(f"\nIniciando verificação ({mode})...", fg=typer.colors.CYAN)
    run_restic(cmd)


def do_ls() -> None:
    """Navegação/inspeção de arquivos nos snapshots."""
    snapshots = get_snapshots()
    if not snapshots:
        typer.secho("Nenhum snapshot encontrado.", fg=typer.colors.YELLOW)
        return

    choices = []
    for snap in snapshots:
        short_id = snap["id"][:8]
        time_str = snap["time"][:19].replace("T", " ")
        paths_str = ", ".join(snap.get("paths", []))
        label = f"[{short_id}] {time_str} - {paths_str}"
        choices.append(questionary.Choice(title=label, value=snap["id"]))

    snap_id = questionary.select(
        "Selecione o snapshot para listar os arquivos:",
        choices=choices
    ).ask()

    if not snap_id:
        return

    profile = get_profile()
    repo = profile.get("restic", {}).get("repo")

    typer.secho(f"\nListando arquivos do snapshot {snap_id[:8]}...", fg=typer.colors.CYAN)
    run_restic(["-r", repo, "ls", snap_id])


def edit_config() -> None:
    """Edita a configuração de caminhos e exclusões."""
    config = load_config()
    profile = get_profile()
    restic_config = profile.get("restic", {})

    repo = questionary.path("Repositório:", default=restic_config.get("repo", "")).ask()
    if repo is None:
        return

    source = questionary.path("Origem (backup):", default=restic_config.get("source", "")).ask()
    if source is None:
        return

    restore_parent = questionary.path("Pai de restauração:", default=restic_config.get("restore_parent", "")).ask()
    if restore_parent is None:
        return

    exclude_file = questionary.path("Arquivo de exclusões:", default=restic_config.get("exclude_file", "")).ask()
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
    typer.secho("Configuração atualizada com sucesso!", fg=typer.colors.GREEN)


def show_restic_menu() -> None:
    """Ponto de entrada principal para o menu interativo Restic."""
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "RESTIC"])
        typer.echo()
        try:
            choice = questionary.select(
                "Menu Restic — Escolha uma opção:",
                choices=[
                    questionary.Choice("[1] 🧙 Assistente Inicial (Novo Usuário)", "wizard"),
                    questionary.Choice("[2] 💾 Fazer Backup", "backup"),
                    questionary.Choice("[3] 📦 Restaurar Snapshot", "restore"),
                    questionary.Choice("[4] 🔍 Verificar Repositório (check)", "check"),
                    questionary.Choice("[5] 📄 Listar Arquivos (ls)", "ls"),
                    questionary.Choice("[6] ⚙️  Configurar Caminhos", "config"),
                    questionary.Separator(),
                    questionary.Choice("[0] ↩️  Voltar ao menu principal", "exit"),
                ],
                use_shortcuts=False,
                instruction="(Use ↑↓ para navegar, Enter para selecionar)",
            ).ask()

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
            elif choice == "config":
                run_dedicated_screen(["UTILITY BELT", "RESTIC", "CONFIGURAÇÃO"], edit_config)

        except KeyboardInterrupt:
            break
        except Exception as e:
            typer.secho(f"\nOcorreu um erro: {e}", fg=typer.colors.RED)
            break


if __name__ == "__main__":
    show_restic_menu()
