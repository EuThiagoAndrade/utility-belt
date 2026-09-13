"""Gerenciamento de configuração e perfis do Utility Belt."""

from __future__ import annotations

import json
import os
import shutil
import tomllib
from pathlib import Path
from typing import Any

import platformdirs
import tomli_w

APP_NAME = "utility-belt"
APP_AUTHOR = "utility-belt"
SCHEMA_VERSION = 1


def get_config_dir() -> Path:
    """Retorna o diretório de configuração do usuário."""
    path = platformdirs.user_config_path(appname=APP_NAME, appauthor=APP_AUTHOR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_dir() -> Path:
    """Retorna o diretório de dados persistentes do usuário."""
    path = platformdirs.user_data_path(appname=APP_NAME, appauthor=APP_AUTHOR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_dir() -> Path:
    """Retorna o diretório de logs do usuário."""
    path = platformdirs.user_log_path(appname=APP_NAME, appauthor=APP_AUTHOR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_state_dir() -> Path:
    """Retorna o diretório de estado do usuário."""
    path = platformdirs.user_state_path(appname=APP_NAME, appauthor=APP_AUTHOR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_file() -> Path:
    """Retorna o caminho do arquivo config.toml."""
    return get_config_dir() / "config.toml"


def get_default_config() -> dict[str, Any]:
    """Retorna a estrutura padrão de configuração."""
    return {
        "schema_version": SCHEMA_VERSION,
        "default_profile": "padrao",
        "profiles": {
            "padrao": {
                "restic": {
                    "repo": "",
                    "repo_id": "",
                    "source": "",
                    "restore_parent": "",
                    "exclude_file": "",
                }
            }
        },
    }


def load_config() -> dict[str, Any]:
    """Carrega o arquivo config.toml ou retorna o padrão se inexistente."""
    config_file = get_config_file()
    if not config_file.is_file():
        return get_default_config()

    try:
        with config_file.open("rb") as f:
            data = tomllib.load(f)
        if not isinstance(data, dict):
            return get_default_config()
        return data
    except Exception:
        return get_default_config()


def save_config(config: dict[str, Any]) -> None:
    """Salva atomicamente a configuração em config.toml usando tomli-w."""
    config_file = get_config_file()
    config_dir = config_file.parent
    config_dir.mkdir(parents=True, exist_ok=True)

    temp_file = config_file.with_suffix(".tmp")
    with temp_file.open("wb") as f:
        tomli_w.dump(config, f)

    temp_file.replace(config_file)


def get_profile(name: str | None = None) -> dict[str, Any]:
    """Obtém um perfil da configuração atual."""
    config = load_config()
    profile_name = name or config.get("default_profile", "padrao")
    profiles = config.get("profiles", {})
    return profiles.get(profile_name, {})


def set_profile(name: str, profile_data: dict[str, Any]) -> None:
    """Atualiza ou insere um perfil na configuração e salva atomicamente."""
    config = load_config()
    if "profiles" not in config or not isinstance(config["profiles"], dict):
        config["profiles"] = {}
    config["profiles"][name] = profile_data
    save_config(config)


def migrate_legacy_restic_config() -> dict[str, Any] | None:
    """Migra com segurança a configuração legada do ResticMenu se encontrada."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None

    legacy_dir = Path(local_app_data) / "ResticMenu"
    legacy_file = legacy_dir / "config.json"

    if not legacy_file.is_file():
        return None

    try:
        content = json.loads(legacy_file.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            return None

        # Backup da configuração legada
        backup_file = legacy_file.with_suffix(".json.bak")
        if not backup_file.exists():
            shutil.copy2(legacy_file, backup_file)

        # Migrar para o perfil 'restic_legado'
        config = load_config()
        if "profiles" not in config:
            config["profiles"] = {}

        restic_cfg = {
            "repo": content.get("repo", ""),
            "repo_id": content.get("repo_id", ""),
            "source": content.get("source", ""),
            "restore_parent": content.get("restore_parent", ""),
            "exclude_file": content.get("exclude_file", ""),
        }

        config["profiles"]["restic_legado"] = {"restic": restic_cfg}
        save_config(config)
        return restic_cfg
    except Exception:
        return None
