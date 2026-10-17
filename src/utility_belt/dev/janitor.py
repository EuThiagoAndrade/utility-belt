"""Utilitário Janitor para detecção e limpeza rápida de caches de compilação e dependências."""

from __future__ import annotations

import os
import shutil
import stat
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Lista canônica e segura de diretórios efêmeros descartáveis
DEFAULT_TARGET_DIRS: set[str] = {
    "node_modules",
    "target",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".turbo",
    ".gradle",
    "bin",
    "obj",
    ".tox",
    ".parcel-cache",
}


@dataclass
class DiscoveredCache:
    """Metadados de um diretório de cache descoberto."""

    path: Path
    target_name: str
    size_bytes: int
    last_modified: float
    is_active: bool

    @property
    def formatted_size(self) -> str:
        return format_size(self.size_bytes)

    @property
    def formatted_time_ago(self) -> str:
        return format_time_ago(self.last_modified)


def format_size(size_bytes: int) -> str:
    """Formata bytes em unidade legível (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_time_ago(timestamp: float) -> str:
    """Formata um timestamp Unix em descrição temporal relativa em português."""
    if timestamp <= 0:
        return "data desconhecida"

    now = time.time()
    diff = max(0.0, now - timestamp)
    days = int(diff // 86400)

    if days == 0:
        hours = int(diff // 3600)
        if hours == 0:
            return "ativo recentemente (hoje)"
        return f"ativo há {hours}h"
    elif days == 1:
        return "ativo há 1 dia"
    elif days < 30:
        return f"sem atividade há {days} dias"
    elif days < 365:
        months = max(1, days // 30)
        return f"sem atividade há {months} {'mês' if months == 1 else 'meses'}"
    else:
        years = max(1, days // 365)
        return f"sem atividade há {years} {'ano' if years == 1 else 'anos'}"


def calculate_dir_size(path: Path) -> tuple[int, float]:
    """Calcula o tamanho total em bytes e o maior timestamp de modificação dos arquivos."""
    total_size = 0
    max_mtime = 0.0

    try:
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    st = os.stat(fp, follow_symlinks=False)
                    total_size += st.st_size
                    if st.st_mtime > max_mtime:
                        max_mtime = st.st_mtime
                except OSError:
                    pass
    except OSError:
        pass

    if max_mtime == 0.0:
        try:
            max_mtime = path.stat().st_mtime
        except OSError:
            pass

    return total_size, max_mtime


def scan_caches(
    root_path: Path,
    target_dirs: set[str] | None = None,
    days_threshold: int = 30,
) -> list[DiscoveredCache]:
    """Varre recursivamente o diretório raiz com poda de busca.

    Crucial: Ao encontrar uma pasta em target_dirs, não desce internamente nela,
    economizando tempo e preservando performance. Também nunca desce dentro de .git.
    """
    if target_dirs is None:
        target_dirs = DEFAULT_TARGET_DIRS

    root_resolved = root_path.resolve()
    if not root_resolved.is_dir():
        return []

    results: list[DiscoveredCache] = []
    now = time.time()
    threshold_seconds = days_threshold * 86400

    for root, dirs, _ in os.walk(root_resolved):
        # Ignora e não percorre o diretório interno do git
        if ".git" in dirs:
            dirs.remove(".git")

        to_remove = []
        for d in dirs:
            if d in target_dirs:
                target_path = Path(root) / d
                size, mtime = calculate_dir_size(target_path)
                is_active = (now - mtime) < threshold_seconds if mtime > 0 else False
                results.append(
                    DiscoveredCache(
                        path=target_path,
                        target_name=d,
                        size_bytes=size,
                        last_modified=mtime,
                        is_active=is_active,
                    )
                )
                to_remove.append(d)

        # Remove da lista de dirs para podar a árvore de busca
        for d in to_remove:
            dirs.remove(d)

    # Ordena por tamanho decrescente
    return sorted(results, key=lambda c: c.size_bytes, reverse=True)


def _handle_remove_readonly(func, path, exc_info):
    """Callback de remoção para contornar arquivos somente-leitura no Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def delete_cache(
    cache_path: Path,
    dry_run: bool = False,
    target_dirs: set[str] | None = None,
) -> tuple[bool, str]:
    """Exclui com segurança um diretório de cache identificado.

    Verifica se o nome do diretório pertence à allowlist antes de qualquer exclusão.
    Retorna uma tupla (sucesso, mensagem_de_erro).
    """
    if target_dirs is None:
        target_dirs = DEFAULT_TARGET_DIRS

    if cache_path.name not in target_dirs:
        return False, f"Diretório '{cache_path.name}' não está na allowlist de segurança."

    if dry_run:
        return True, "Simulado (--dry-run)"

    try:
        str_path = str(cache_path.resolve())
        # Suporte a caminhos longos no Windows (> 260 chars)
        if sys.platform == "win32" and not str_path.startswith("\\\\?\\") and len(str_path) >= 240:
            str_path = "\\\\?\\" + str_path

        shutil.rmtree(str_path, onerror=_handle_remove_readonly)
        return True, ""
    except Exception as err:
        return False, str(err)
