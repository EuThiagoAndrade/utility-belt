"""Testes para o módulo de configuração do Utility Belt."""

import json
from pathlib import Path
from unittest.mock import patch

from utility_belt.config import (
    get_default_config,
    get_profile,
    load_config,
    migrate_legacy_restic_config,
    save_config,
    set_profile,
)


def test_default_config() -> None:
    cfg = get_default_config()
    assert cfg["schema_version"] == 1
    assert "default_profile" in cfg
    assert "profiles" in cfg


def test_save_and_load_config(tmp_path: Path) -> None:
    fake_config_file = tmp_path / "config.toml"

    with patch("utility_belt.config.get_config_file", return_value=fake_config_file):
        initial = load_config()
        assert initial["default_profile"] == "padrao"

        initial["default_profile"] = "trabalho"
        save_config(initial)

        assert fake_config_file.is_file()
        reloaded = load_config()
        assert reloaded["default_profile"] == "trabalho"


def test_set_and_get_profile(tmp_path: Path) -> None:
    fake_config_file = tmp_path / "config.toml"

    with patch("utility_belt.config.get_config_file", return_value=fake_config_file):
        profile_data = {
            "restic": {
                "repo": "/tmp/repo",
                "repo_id": "test-id-123",
                "source": "/tmp/source",
            }
        }
        set_profile("casa", profile_data)

        retrieved = get_profile("casa")
        assert retrieved["restic"]["repo_id"] == "test-id-123"


def test_migrate_legacy_restic_config(tmp_path: Path, monkeypatch) -> None:
    legacy_dir = tmp_path / "ResticMenu"
    legacy_dir.mkdir(parents=True)
    legacy_json = legacy_dir / "config.json"

    legacy_data = {
        "repo": "D:\\Restic-Programas",
        "repo_id": "repo-abc-123",
        "source": "C:\\Programas",
        "restore_parent": "C:\\Programas_bkp",
        "exclude_file": "",
    }
    legacy_json.write_text(json.dumps(legacy_data), encoding="utf-8")

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    fake_config_file = tmp_path / "belt_config.toml"
    with patch("utility_belt.config.get_config_file", return_value=fake_config_file):
        migrated = migrate_legacy_restic_config()
        assert migrated is not None
        assert migrated["repo_id"] == "repo-abc-123"
        assert migrated["source"] == "C:\\Programas"

        # Verifica se o backup foi criado
        assert (legacy_dir / "config.json.bak").is_file()

        # Verifica se foi gravado no config.toml
        cfg = load_config()
        assert "restic_legado" in cfg["profiles"]
        assert cfg["profiles"]["restic_legado"]["restic"]["repo_id"] == "repo-abc-123"
