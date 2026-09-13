"""Mecanismo de execução de ferramentas do Utility Belt."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from utility_belt.catalog import CURRENT_PLATFORM, ToolManifest

# Códigos padronizados do Launcher
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_PRECONDITION_FAILED = 2
EXIT_INTERRUPTED = 130


class RunnerError(Exception):
    def __init__(self, message: str, exit_code: int = EXIT_PRECONDITION_FAILED):
        super().__init__(message)
        self.exit_code = exit_code


def resolve_runtime_command(manifest: ToolManifest, args: list[str]) -> list[str]:
    """Resolve a lista de comandos e argumentos para o subprocesso."""
    entry_path = manifest.entry_path
    if not entry_path or not entry_path.exists():
        raise RunnerError(f"Arquivo de entrada da ferramenta '{manifest.id}' não encontrado: {entry_path}")

    runtime = manifest.runtime.lower()

    if runtime == "python":
        return [sys.executable, str(entry_path)] + args

    if runtime == "powershell":
        exe = shutil.which("pwsh") or shutil.which("powershell")
        if not exe:
            raise RunnerError("PowerShell ('pwsh' ou 'powershell') não encontrado no PATH.")
        return [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(entry_path)] + args

    if runtime == "bash":
        exe = shutil.which("bash") or shutil.which("sh")
        if not exe:
            raise RunnerError("Interpretador 'bash' ou 'sh' não encontrado no PATH.")
        return [exe, str(entry_path)] + args

    if runtime == "binary":
        return [str(entry_path)] + args

    raise RunnerError(f"Runtime '{runtime}' não suportado.")


def run_tool(
    manifest: ToolManifest,
    args: list[str] | None = None,
    non_interactive: bool = False,
    extra_env: dict[str, str] | None = None,
) -> int:
    """
    Executa a ferramenta mantendo o isolamento, preservando o cwd do usuário
    e tratando cancelamento e códigos de saída.
    """
    args = args or []

    # 1. Validação de Plataforma
    if not manifest.is_compatible:
        print(
            f"Erro: A ferramenta '{manifest.id}' é compatível apenas com [{', '.join(manifest.platforms)}], "
            f"mas o sistema atual é '{CURRENT_PLATFORM}'.",
            file=sys.stderr,
        )
        return EXIT_PRECONDITION_FAILED

    # 2. Validação de TTY e Interatividade
    is_tty = sys.stdin.isatty()
    if manifest.interactive and (not is_tty or non_interactive):
        print(
            f"Erro: A ferramenta '{manifest.id}' é interativa e requer um terminal (TTY), "
            "ou utilize subcomandos CLI não interativos.",
            file=sys.stderr,
        )
        return EXIT_PRECONDITION_FAILED

    # 3. Preparação dos Argumentos
    try:
        cmd = resolve_runtime_command(manifest, args)
    except RunnerError as err:
        print(f"Erro ao inicializar ferramenta '{manifest.id}': {err}", file=sys.stderr)
        return err.exit_code

    # 4. Ambiente do Subprocesso
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    # Injeção de PYTHONPATH para permitir imports locais da ferramenta
    if manifest.tool_dir:
        existing_pythonpath = env.get("PYTHONPATH", "")
        tool_dir_str = str(manifest.tool_dir)
        env["PYTHONPATH"] = (
            f"{tool_dir_str}{os.pathsep}{existing_pythonpath}"
            if existing_pythonpath
            else tool_dir_str
        )

    # Garante saída em UTF-8 no Windows para subprocessos Python
    if sys.platform == "win32":
        env["PYTHONIOENCODING"] = "utf-8"

    # 5. Execução do Subprocesso
    # O cwd é SEMPRE o diretório atual do usuário para que caminhos relativos funcionem
    user_cwd = Path.cwd()

    try:
        has_fileno = True
        try:
            sys.stdout.fileno()
        except (AttributeError, OSError, ValueError):
            has_fileno = False

        if has_fileno:
            result = subprocess.run(
                cmd,
                cwd=user_cwd,
                env=env,
                shell=False,
            )
            return result.returncode
        else:
            result = subprocess.run(
                cmd,
                cwd=user_cwd,
                env=env,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.stdout:
                sys.stdout.write(result.stdout)
                sys.stdout.flush()
            if result.stderr:
                sys.stderr.write(result.stderr)
                sys.stderr.flush()
            return result.returncode
    except KeyboardInterrupt:
        print("\nOperação interrompida pelo usuário (Ctrl+C).", file=sys.stderr)
        return EXIT_INTERRUPTED
    except FileNotFoundError as err:
        print(f"Erro: executável não encontrado para '{manifest.id}': {err}", file=sys.stderr)
        return EXIT_PRECONDITION_FAILED
    except Exception as err:
        print(f"Erro inesperado ao executar '{manifest.id}': {err}", file=sys.stderr)
        return EXIT_ERROR
