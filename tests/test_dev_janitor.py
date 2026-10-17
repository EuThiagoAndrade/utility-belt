"""Testes para o utilitário Janitor (limpeza de caches de compilação e dependências)."""

from __future__ import annotations

import os
import stat
import time
from pathlib import Path

from utility_belt.dev.janitor import (
    calculate_dir_size,
    delete_cache,
    format_size,
    format_time_ago,
    scan_caches,
)


def test_format_size() -> None:
    assert format_size(500) == "500 B"
    assert format_size(2048) == "2.0 KB"
    assert format_size(10 * 1024 * 1024) == "10.0 MB"
    assert format_size(2 * 1024 * 1024 * 1024) == "2.00 GB"


def test_format_time_ago() -> None:
    now = time.time()
    assert "hoje" in format_time_ago(now - 100)
    assert "dias" in format_time_ago(now - 5 * 86400)
    assert "meses" in format_time_ago(now - 90 * 86400)
    assert "ano" in format_time_ago(now - 400 * 86400)
    assert format_time_ago(0) == "data desconhecida"


def test_calculate_dir_size(tmp_path: Path) -> None:
    cache_dir = tmp_path / "node_modules"
    cache_dir.mkdir()
    (cache_dir / "file1.txt").write_bytes(b"A" * 100)
    (cache_dir / "file2.txt").write_bytes(b"B" * 200)

    size, mtime = calculate_dir_size(cache_dir)
    assert size == 300
    assert mtime > 0


def test_scan_caches_with_pruning_and_git_ignore(tmp_path: Path) -> None:
    # Cria projeto com node_modules, .venv e .git
    project = tmp_path / "my_project"
    project.mkdir()

    # node_modules com outro node_modules interno (deve podar e retornar apenas o raiz)
    nm = project / "node_modules"
    nm.mkdir()
    (nm / "pkg1.txt").write_bytes(b"12345")
    nested_nm = nm / "nested" / "node_modules"
    nested_nm.mkdir(parents=True)
    (nested_nm / "pkg2.txt").write_bytes(b"67890")

    # .venv
    venv = project / ".venv"
    venv.mkdir()
    (venv / "python.exe").write_bytes(b"dummy")

    # .git com node_modules falso (deve ser totalmente ignorado)
    git_dir = project / ".git" / "node_modules"
    git_dir.mkdir(parents=True)
    (git_dir / "ignored.txt").write_bytes(b"secret")

    # Executa a varredura
    results = scan_caches(project)

    found_names = [c.path.name for c in results]
    assert "node_modules" in found_names
    assert ".venv" in found_names
    assert len(results) == 2  # Apenas os 2 alvos de nível superior (poda funcionou e .git foi ignorado)

    # Garante que o tamanho do node_modules engloba os arquivos internos
    nm_result = next(c for c in results if c.path.name == "node_modules")
    assert nm_result.size_bytes == 10  # 5 + 5 bytes


def test_scan_caches_activity_heuristic(tmp_path: Path) -> None:
    project = tmp_path / "my_project"
    project.mkdir()

    # Cache ativo (modificado agora)
    active_cache = project / ".pytest_cache"
    active_cache.mkdir()
    active_file = active_cache / "test.txt"
    active_file.write_text("ok")

    # Cache inativo (modificado há 60 dias)
    inactive_cache = project / "target"
    inactive_cache.mkdir()
    inactive_file = inactive_cache / "build.txt"
    inactive_file.write_text("old")
    old_time = time.time() - (60 * 86400)
    os.utime(inactive_file, (old_time, old_time))
    os.utime(inactive_cache, (old_time, old_time))

    results = scan_caches(project, days_threshold=30)
    active_item = next(c for c in results if c.target_name == ".pytest_cache")
    inactive_item = next(c for c in results if c.target_name == "target")

    assert active_item.is_active is True
    assert inactive_item.is_active is False


def test_delete_cache_allowlist_protection(tmp_path: Path) -> None:
    forbidden_dir = tmp_path / "important_source_code"
    forbidden_dir.mkdir()
    (forbidden_dir / "main.py").write_text("print('hello')")

    ok, err = delete_cache(forbidden_dir)
    assert ok is False
    assert "allowlist" in err
    assert forbidden_dir.is_dir()


def test_delete_cache_dry_run(tmp_path: Path) -> None:
    target_dir = tmp_path / "node_modules"
    target_dir.mkdir()
    (target_dir / "dep.txt").write_text("lib")

    ok, msg = delete_cache(target_dir, dry_run=True)
    assert ok is True
    assert "dry-run" in msg
    assert target_dir.is_dir()


def test_delete_cache_real_with_readonly_files(tmp_path: Path) -> None:
    target_dir = tmp_path / ".venv"
    target_dir.mkdir()
    ro_file = target_dir / "readonly.txt"
    ro_file.write_text("immutable")

    # Marca arquivo como somente-leitura
    os.chmod(ro_file, stat.S_IREAD)

    ok, err = delete_cache(target_dir, dry_run=False)
    assert ok is True
    assert err == ""
    assert not target_dir.exists()
