#!/usr/bin/env python3
"""Módulo Restic seguro: preservação estrita de repo_id, overlaps e senhas em memória."""

from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from utility_belt.config import (
    get_log_dir,
    get_profile,
    load_config,
    migrate_legacy_restic_config,
    save_config,
)


def overlaps(a: Path | str, b: Path | str) -> bool:
    """Verifica se um caminho contém ou é contido por outro."""
    pa, pb = Path(a).resolve(), Path(b).resolve()
    return pa == pb or pa in pb.parents or pb in pa.parents


def record_audit(command_args: list[str], event: str, code: int | None = None) -> None:
    """Registra auditoria em arquivo JSONL sem gravar senhas."""
    try:
        log_file = get_log_dir() / "restic_operacoes.jsonl"
        entry = {
            "timestamp": dt.datetime.now().isoformat(),
            "event": event,
            "command": [arg for arg in command_args if not arg.startswith("--password")],
            "returncode": code,
        }
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


class ResticController:
    def __init__(self, repo: str, repo_id: str = "", non_interactive: bool = False):
        self.exe = shutil.which("restic")
        if not self.exe:
            raise ValueError("Executável 'restic' não encontrado no PATH.")

        self.repo = str(Path(repo).resolve())
        self.expected_repo_id = repo_id
        self.non_interactive = non_interactive
        self._password: str | None = os.environ.get("RESTIC_PASSWORD")

    def get_password(self) -> str:
        """Obtém a senha da memória ou prompt seguro."""
        if self._password:
            return self._password

        if self.non_interactive:
            raise ValueError(
                "Modo não-interativo ativo mas a variável de ambiente RESTIC_PASSWORD não foi informada."
            )

        self._password = getpass.getpass("Senha do repositório Restic (não será salva em disco): ")
        return self._password

    def run_restic(self, args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Executa um comando Restic com senha injetada via ambiente temporário."""
        pwd = self.get_password()
        env = os.environ.copy()
        env["RESTIC_PASSWORD"] = pwd

        cmd = [self.exe, "-r", self.repo] + args
        record_audit(cmd, "inicio")

        try:
            res = subprocess.run(
                cmd,
                env=env,
                capture_output=capture_output,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            record_audit(cmd, "fim", code=res.returncode)
            return res
        except KeyboardInterrupt:
            record_audit(cmd, "interrompido", code=130)
            raise

    def check_repo_exists(self) -> bool:
        """Verifica se o diretório do repositório contém o arquivo config."""
        return (Path(self.repo) / "config").is_file()

    def verify_repo_id(self) -> None:
        """Confere a identidade interna do repositório para evitar HD trocado."""
        if not self.check_repo_exists():
            raise ValueError(
                f"Repositório inexistente ou inacessível em '{self.repo}'. "
                "Verifique a unidade e use 'init' se for criá-lo deliberadamente."
            )

        if not self.expected_repo_id:
            return

        res = self.run_restic(["cat", "config"], capture_output=True)
        if res.returncode != 0:
            raise ValueError(f"Não foi possível ler a configuração do repositório (código {res.returncode}).")

        try:
            cfg_data = json.loads(res.stdout)
            actual_id = cfg_data.get("id", "")
            if actual_id != self.expected_repo_id:
                raise ValueError(
                    f"SEGURANÇA: O ID do repositório no disco ({actual_id[:8]}...) "
                    f"não confere com o configurado ({self.expected_repo_id[:8]}...). "
                    "Operação abortada para evitar gravação no HD/repositório incorreto!"
                )
        except json.JSONDecodeError:
            raise ValueError("Configuração do repositório retornou JSON inválido.")


def cmd_backup(args: argparse.Namespace) -> int:
    profile = get_profile(args.profile).get("restic", {})
    repo = args.repo or profile.get("repo")
    repo_id = profile.get("repo_id", "")
    source = args.source or profile.get("source")
    exclude_file = args.exclude_file or profile.get("exclude_file")

    if not repo:
        print("Erro: Repositório não informado via --repo ou perfil.", file=sys.stderr)
        return 1
    if not source:
        print("Erro: Pasta de origem não informada via --source ou perfil.", file=sys.stderr)
        return 1

    source_path = Path(source).resolve()
    repo_path = Path(repo).resolve()

    if not source_path.exists():
        print(f"Erro: Pasta de origem '{source_path}' não existe.", file=sys.stderr)
        return 1

    # Salvaguarda fundamental de sobreposição
    if overlaps(source_path, repo_path):
        print(
            f"Erro: A pasta de origem '{source_path}' e o repositório '{repo_path}' estão sobrepostos!",
            file=sys.stderr,
        )
        return 2

    try:
        controller = ResticController(str(repo_path), repo_id=repo_id, non_interactive=args.non_interactive)
        controller.verify_repo_id()
    except ValueError as err:
        print(f"Erro: {err}", file=sys.stderr)
        return 2

    restic_args = ["backup", str(source_path)]
    if exclude_file and Path(exclude_file).is_file():
        restic_args += ["--exclude-file", str(exclude_file)]
    if args.dry_run:
        restic_args.append("--dry-run")

    print("\nIniciando backup Restic...")
    print(f" Origem      : {source_path}")
    print(f" Repositório : {repo_path}")
    if args.dry_run:
        print(" [DRY-RUN ATIVO]")

    try:
        proc = controller.run_restic(restic_args)
    except ValueError as err:
        print(f"Erro: {err}", file=sys.stderr)
        return 2

    if proc.returncode == 3:
        print(
            "\nAVISO [CÓDIGO 3]: Backup finalizado, mas alguns arquivos não puderam ser lidos (backup incompleto).",
            file=sys.stderr,
        )
        return 3
    elif proc.returncode != 0:
        print(f"\nErro no backup do Restic (código {proc.returncode}).", file=sys.stderr)
        return proc.returncode

    print("\nBackup concluído com sucesso!")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    profile = get_profile(args.profile).get("restic", {})
    repo = args.repo or profile.get("repo")
    repo_id = profile.get("repo_id", "")
    target = args.target or profile.get("restore_parent")

    if not repo:
        print("Erro: Repositório não informado via --repo ou perfil.", file=sys.stderr)
        return 1
    if not target:
        print("Erro: Destino da restauração não informado via --target ou perfil.", file=sys.stderr)
        return 1

    target_path = Path(target).resolve()
    repo_path = Path(repo).resolve()

    if overlaps(target_path, repo_path):
        print(
            f"Erro: O destino da restauração '{target_path}' e o repositório '{repo_path}' estão sobrepostos!",
            file=sys.stderr,
        )
        return 2

    try:
        controller = ResticController(str(repo_path), repo_id=repo_id, non_interactive=args.non_interactive)
        controller.verify_repo_id()
    except ValueError as err:
        print(f"Erro: {err}", file=sys.stderr)
        return 2

    snapshot = args.snapshot or "latest"
    restic_args = ["restore", snapshot, "--target", str(target_path)]
    if args.include:
        restic_args += ["--include", args.include]
    if args.dry_run:
        restic_args.append("--dry-run")

    target_path.mkdir(parents=True, exist_ok=True)
    print(f"\nIniciando restauração Restic do snapshot '{snapshot}' em '{target_path}'...")
    proc = controller.run_restic(restic_args)
    return proc.returncode


def cmd_check(args: argparse.Namespace) -> int:
    profile = get_profile(args.profile).get("restic", {})
    repo = args.repo or profile.get("repo")
    repo_id = profile.get("repo_id", "")

    if not repo:
        print("Erro: Repositório não informado.", file=sys.stderr)
        return 1

    try:
        controller = ResticController(str(repo), repo_id=repo_id)
        controller.verify_repo_id()
    except ValueError as err:
        print(f"Erro: {err}", file=sys.stderr)
        return 2

    restic_args = ["check"]
    if args.read_data:
        restic_args.append("--read-data")

    print(f"\nVerificando integridade do repositório '{repo}'...")
    proc = controller.run_restic(restic_args)
    return proc.returncode


def cmd_snapshots(args: argparse.Namespace) -> int:
    profile = get_profile(args.profile).get("restic", {})
    repo = args.repo or profile.get("repo")
    repo_id = profile.get("repo_id", "")

    if not repo:
        print("Erro: Repositório não informado.", file=sys.stderr)
        return 1

    try:
        controller = ResticController(str(repo), repo_id=repo_id)
        controller.verify_repo_id()
    except ValueError as err:
        print(f"Erro: {err}", file=sys.stderr)
        return 2

    proc = controller.run_restic(["snapshots"])
    return proc.returncode


def cmd_init(args: argparse.Namespace) -> int:
    repo = args.repo
    if not repo:
        print("Erro: Repositório obrigatório para init.", file=sys.stderr)
        return 1

    repo_path = Path(repo).resolve()
    if (repo_path / "config").is_file():
        print(f"Erro: O repositório em '{repo_path}' já existe!", file=sys.stderr)
        return 1

    controller = ResticController(str(repo_path))
    print(f"\nInicializando deliberadamente um novo repositório em '{repo_path}'...")
    proc = controller.run_restic(["init"])
    if proc.returncode == 0:
        # Lê o ID recém-criado
        cat_proc = controller.run_restic(["cat", "config"], capture_output=True)
        if cat_proc.returncode == 0:
            cfg = json.loads(cat_proc.stdout)
            new_id = cfg.get("id", "")
            print(f"\nRepositório criado com sucesso! ID: {new_id}")
            if args.profile:
                cur_cfg = load_config()
                if args.profile not in cur_cfg.get("profiles", {}):
                    cur_cfg.setdefault("profiles", {})[args.profile] = {}
                cur_cfg["profiles"][args.profile].setdefault("restic", {})["repo"] = str(repo_path)
                cur_cfg["profiles"][args.profile]["restic"]["repo_id"] = new_id
                save_config(cur_cfg)
                print(f"Configuração do perfil '{args.profile}' atualizada com o ID.")
    return proc.returncode


def cmd_migrate_config() -> int:
    print("Tentando migrar configuração legada do ResticMenu...")
    migrated = migrate_legacy_restic_config()
    if migrated:
        print("Sucesso! Configuração migrada para o perfil 'restic_legado':")
        print(f" Repositório : {migrated.get('repo')}")
        print(f" Repo ID     : {migrated.get('repo_id')}")
        print(f" Origem      : {migrated.get('source')}")
        return 0
    else:
        print("Nenhuma configuração legada encontrada ou erro na leitura.")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Operações Restic protegidas")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Backup
    p_backup = subparsers.add_parser("backup", help="Executa backup incremental")
    p_backup.add_argument("--repo", help="Caminho do repositório")
    p_backup.add_argument("--source", help="Pasta de origem")
    p_backup.add_argument("--exclude-file", help="Arquivo de exclusões")
    p_backup.add_argument("--profile", help="Nome do perfil de configuração")
    p_backup.add_argument("--non-interactive", action="store_true", help="Proíbe prompts interativos")
    p_backup.add_argument("--dry-run", action="store_true", help="Simula o backup")

    # Restore
    p_restore = subparsers.add_parser("restore", help="Restaura arquivos de um snapshot")
    p_restore.add_argument("--snapshot", default="latest", help="ID do snapshot ou 'latest'")
    p_restore.add_argument("--target", help="Pasta de destino")
    p_restore.add_argument("--repo", help="Caminho do repositório")
    p_restore.add_argument("--include", help="Filtro de arquivos/pastas")
    p_restore.add_argument("--profile", help="Nome do perfil de configuração")
    p_restore.add_argument("--non-interactive", action="store_true")
    p_restore.add_argument("--dry-run", action="store_true")

    # Check
    p_check = subparsers.add_parser("check", help="Verifica integridade do repositório")
    p_check.add_argument("--repo", help="Caminho do repositório")
    p_check.add_argument("--profile", help="Nome do perfil de configuração")
    p_check.add_argument("--read-data", action="store_true", help="Lê todos os dados dos packs")

    # Snapshots
    p_snap = subparsers.add_parser("snapshots", help="Lista snapshots do repositório")
    p_snap.add_argument("--repo", help="Caminho do repositório")
    p_snap.add_argument("--profile", help="Nome do perfil de configuração")

    # Init
    p_init = subparsers.add_parser("init", help="Inicializa novo repositório deliberadamente")
    p_init.add_argument("--repo", required=True, help="Caminho do novo repositório")
    p_init.add_argument("--profile", help="Perfil onde salvar o ID gerado")

    # Migrate config
    subparsers.add_parser("migrate-config", help="Migra config do ResticMenu para config.toml")

    args = parser.parse_args()

    if args.subcommand == "backup":
        return cmd_backup(args)
    elif args.subcommand == "restore":
        return cmd_restore(args)
    elif args.subcommand == "check":
        return cmd_check(args)
    elif args.subcommand == "snapshots":
        return cmd_snapshots(args)
    elif args.subcommand == "init":
        return cmd_init(args)
    elif args.subcommand == "migrate-config":
        return cmd_migrate_config()
    return 1


if __name__ == "__main__":
    sys.exit(main())
