"""Diagnóstico de ambiente e dependências do Utility Belt."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from typing import Any

from utility_belt.catalog import CURRENT_PLATFORM
from utility_belt.config import get_config_file, load_config


def check_executable(name: str) -> dict[str, Any]:
    """Verifica se um executável está presente no PATH."""
    path = shutil.which(name)
    return {
        "installed": path is not None,
        "path": path or "",
    }


def check_docker() -> dict[str, Any]:
    """Verifica executável do Docker e se o daemon está respondendo."""
    info = check_executable("docker")
    if not info["installed"]:
        info["daemon_running"] = False
        info["details"] = "Docker não encontrado no PATH."
        return info

    try:
        res = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            info["daemon_running"] = True
            info["details"] = f"Daemon ativo (versão {res.stdout.strip()})"
        else:
            info["daemon_running"] = False
            info["details"] = "Daemon Docker inacessível ou parado."
    except subprocess.TimeoutExpired:
        info["daemon_running"] = False
        info["details"] = "Timeout ao consultar daemon do Docker."
    except Exception as err:
        info["daemon_running"] = False
        info["details"] = f"Erro ao verificar Docker: {err}"

    return info


def check_restic() -> dict[str, Any]:
    """Verifica executável do Restic e sua versão."""
    info = check_executable("restic")
    if not info["installed"]:
        info["details"] = "Restic não encontrado no PATH."
        return info

    try:
        res = subprocess.run(
            ["restic", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            info["details"] = res.stdout.splitlines()[0]
        else:
            info["details"] = "Erro ao obter versão do Restic."
    except Exception as err:
        info["details"] = f"Erro ao executar Restic: {err}"

    return info


def run_diagnostics() -> dict[str, Any]:
    """Executa todos os testes de diagnóstico do ambiente."""
    cfg_file = get_config_file()
    cfg = load_config()

    return {
        "system": {
            "platform": CURRENT_PLATFORM,
            "os_name": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
        },
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
            "compatible": sys.version_info >= (3, 11),
        },
        "config": {
            "path": str(cfg_file),
            "exists": cfg_file.is_file(),
            "default_profile": cfg.get("default_profile", "padrao"),
            "profiles_count": len(cfg.get("profiles", {})),
        },
        "dependencies": {
            "git": check_executable("git"),
            "docker": check_docker(),
            "restic": check_restic(),
            "powershell": check_executable("pwsh") if shutil.which("pwsh") else check_executable("powershell"),
            "bash": check_executable("bash"),
        },
    }
