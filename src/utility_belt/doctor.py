"""Diagnóstico de ambiente e dependências do Utility Belt."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from typing import Any

import platformdirs

from utility_belt.catalog import CURRENT_PLATFORM
from utility_belt.config import APP_AUTHOR, APP_NAME, get_config_file, load_config


def check_markdown() -> dict[str, Any]:
    """Somente lê o runtime: sem mkdir, lock, aquisição ou consentimento."""
    from utility_belt.markdown_runtime.runtime import RECIPES, Runtime

    data = platformdirs.user_data_path(appname=APP_NAME, appauthor=APP_AUTHOR)
    runtime = Runtime(None, data_dir=data)
    environments = {}
    for environment in ("core", "audio"):
        interpreter = runtime.python(environment)
        groups = {}
        if interpreter.is_file():
            script = (
                "import importlib,importlib.metadata,importlib.util,json;"
                f"recipes={RECIPES['groups']!r};result={{}};"
                "\nfor group,recipe in recipes.items():"
                "\n try:"
                "\n  assert importlib.metadata.version('markitdown')=='0.1.8'"
                "\n  [importlib.import_module(name) for name in recipe['imports']]"
                "\n  result[group]=True"
                "\n except Exception: result[group]=False"
                f"\nif {environment!r}=='core' and any(importlib.util.find_spec(n) for n in ('speech_recognition','pydub')): result['base']=False"
                "\nprint(json.dumps(result))"
            )
            try:
                import json
                response = subprocess.run([str(interpreter), "-I", "-B", "-c", script],
                                          capture_output=True, text=True, timeout=15)
                if response.returncode == 0:
                    groups = json.loads(response.stdout)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                pass
        environments[environment] = {"python": str(interpreter), "groups": groups}
    installed = bool(environments["core"]["groups"].get("base"))
    import os
    exiftool = runtime.root / "exiftool-13.59" / ("exiftool.exe" if os.name == "nt" else "Image-ExifTool-13.59/exiftool")
    return {"installed": installed, "path": str(runtime.root), "environments": environments,
            "binaries": {"exiftool_portable": str(exiftool) if exiftool.is_file() else "",
                         "exiftool_path": shutil.which("exiftool") or "",
                         "ffmpeg_path": shutil.which("ffmpeg") or ""},
            "compatible": (3, 11) <= sys.version_info[:2] <= (3, 14),
            "details": "MarkItDown 0.1.8 disponível" if installed else
                       "Motor não adquirido/indisponível; execute belt markdown convert em TTY para consentir. Python 3.11–3.14."}


def check_clipboard() -> dict[str, Any]:
    """Não lê nem altera o conteúdo; informa somente o backend da sessão."""
    import os

    if sys.platform == "win32":
        available = True
        detail = "Backend Windows; acesso depende da sessão e da disponibilidade do clipboard."
    else:
        available = bool((os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-paste") and shutil.which("wl-copy"))
                         or (os.environ.get("DISPLAY") and (shutil.which("xclip") or shutil.which("xsel"))))
        detail = "Linux requer sessão gráfica e backend xclip/xsel ou wl-copy/wl-paste; headless pode ser indisponível."
    return {"installed": available, "details": detail}


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
        info["install_guide"] = (
            "Instale com 'winget install Docker.DockerDesktop' ou baixe em https://www.docker.com/products/docker-desktop"
            if sys.platform == "win32"
            else "Instale seguindo o guia em https://docs.docker.com/engine/install/"
        )
        info["download_url"] = "https://www.docker.com/products/docker-desktop"
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
            info["install_guide"] = (
                "Inicie o Docker Desktop para habilitar o daemon."
                if sys.platform == "win32"
                else "Inicie o serviço com: sudo systemctl start docker"
            )
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
        info["install_guide"] = (
            "Instale com 'winget install restic.restic' ou baixe em https://github.com/restic/restic/releases"
            if sys.platform == "win32"
            else "Instale com 'sudo apt install restic' ou baixe em https://github.com/restic/restic/releases"
        )
        info["download_url"] = "https://restic.net"
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
            "markdown": check_markdown(),
            "clipboard": check_clipboard(),
        },
    }
