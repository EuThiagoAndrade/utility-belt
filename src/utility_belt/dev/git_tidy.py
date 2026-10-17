"""Utilitário Git-Tidy para higienização inteligente de branches locais e remotas."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

PROTECTED_BRANCH_NAMES: set[str] = {
    "main",
    "master",
    "dev",
    "develop",
    "development",
    "staging",
    "stage",
    "production",
    "prod",
}


@dataclass
class LocalBranchInfo:
    """Informações e classificação de uma branch local."""

    name: str
    is_current: bool
    is_protected: bool
    is_merged: bool
    is_gone: bool

    @property
    def is_eligible_for_deletion(self) -> bool:
        """Determina se a branch é segura para remoção automática ou sugerida."""
        return not self.is_current and not self.is_protected and (self.is_merged or self.is_gone)

    @property
    def status_label(self) -> str:
        if self.is_current:
            return "[Atual / HEAD]"
        if self.is_protected:
            return "[Protegida]"
        if self.is_merged:
            return "[Mergeada]"
        if self.is_gone:
            return "[Remoto removido / Squash]"
        return "[Trabalho pendente]"


@dataclass
class RemoteBranchInfo:
    """Informações e classificação de uma branch remota."""

    name: str  # Nome relativo (ex: 'feature/antiga')
    full_ref: str  # Referência completa (ex: 'origin/feature/antiga')
    is_protected: bool
    is_merged: bool

    @property
    def is_eligible_for_deletion(self) -> bool:
        return not self.is_protected and self.is_merged

    @property
    def status_label(self) -> str:
        if self.is_protected:
            return "[Protegida]"
        if self.is_merged:
            return "[Mergeada no remote]"
        return "[Ativa / Não mergeada]"


def is_git_installed() -> bool:
    """Verifica se o binário do Git está presente no PATH."""
    return shutil.which("git") is not None


def run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Executa comando do Git capturando stdout e stderr."""
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def is_inside_git_repo(cwd: Path | None = None) -> bool:
    """Verifica se o diretório de execução está dentro de um repositório Git."""
    if not is_git_installed():
        return False
    res = run_git(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    return res.returncode == 0 and res.stdout.strip() == "true"


def is_protected_branch(branch_name: str) -> bool:
    """Identifica se uma branch possui nome canônico protegido."""
    clean_name = branch_name.replace("origin/", "").strip()
    if clean_name.lower() in PROTECTED_BRANCH_NAMES:
        return True
    if clean_name.startswith("release/") or clean_name.startswith("v"):
        return True
    return False


def get_current_branch(cwd: Path | None = None) -> str:
    """Obtém o nome da branch atual (HEAD)."""
    res = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if res.returncode == 0:
        return res.stdout.strip()
    return ""


def get_default_branch(cwd: Path | None = None) -> str:
    """Identifica a branch padrão do repositório (ex: main ou master)."""
    # Tenta descobrir via origin/HEAD
    res = run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=cwd)
    if res.returncode == 0:
        ref = res.stdout.strip()
        return ref.split("/")[-1]

    # Fallbacks comuns
    local_branches = get_raw_local_branches(cwd)
    if "main" in local_branches:
        return "main"
    if "master" in local_branches:
        return "master"
    return "main"


def get_raw_local_branches(cwd: Path | None = None) -> set[str]:
    """Retorna o conjunto de nomes de branches locais existentes."""
    res = run_git(["for-each-ref", "--format=%(refname:short)", "refs/heads"], cwd=cwd)
    if res.returncode != 0:
        return set()
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def prune_remote(remote: str = "origin", cwd: Path | None = None) -> tuple[bool, str]:
    """Executa sincronização preventiva git fetch --prune."""
    res = run_git(["fetch", "--prune", remote], cwd=cwd)
    if res.returncode == 0:
        return True, ""
    return False, res.stderr.strip()


def get_local_branches(
    default_branch: str | None = None,
    cwd: Path | None = None,
) -> list[LocalBranchInfo]:
    """Analisa e classifica todas as branches locais do repositório."""
    if not is_inside_git_repo(cwd):
        return []

    if default_branch is None:
        default_branch = get_default_branch(cwd)

    current_branch = get_current_branch(cwd)

    # Identifica branches diretamente mergeadas na default_branch
    res_merged = run_git(["branch", "--merged", default_branch], cwd=cwd)
    merged_branches: set[str] = set()
    if res_merged.returncode == 0:
        for line in res_merged.stdout.splitlines():
            name = line.replace("*", "").strip()
            if name:
                merged_branches.add(name)

    # Identifica branches com tracking remoto e status [gone]
    res_tracking = run_git(
        ["for-each-ref", "--format=%(refname:short)|%(upstream:track)", "refs/heads"],
        cwd=cwd,
    )
    gone_branches: set[str] = set()
    if res_tracking.returncode == 0:
        for line in res_tracking.stdout.splitlines():
            if "|" in line:
                name, track = line.split("|", 1)
                name = name.strip()
                if "[gone]" in track:
                    gone_branches.add(name)

    raw_branches = get_raw_local_branches(cwd)
    results: list[LocalBranchInfo] = []

    for name in sorted(raw_branches):
        is_cur = name == current_branch
        is_prot = is_protected_branch(name)
        is_mrg = name in merged_branches
        is_gn = name in gone_branches

        results.append(
            LocalBranchInfo(
                name=name,
                is_current=is_cur,
                is_protected=is_prot,
                is_merged=is_mrg,
                is_gone=is_gn,
            )
        )

    return results


def get_remote_branches(
    remote: str = "origin",
    default_branch: str | None = None,
    cwd: Path | None = None,
) -> list[RemoteBranchInfo]:
    """Analisa e classifica as branches remotas no remote especificado."""
    if not is_inside_git_repo(cwd):
        return []

    if default_branch is None:
        default_branch = get_default_branch(cwd)

    remote_prefix = f"{remote}/"

    # Branches remotas mergeadas na branch principal do remote
    remote_default = f"{remote_prefix}{default_branch}"
    res_merged = run_git(["branch", "-r", "--merged", remote_default], cwd=cwd)
    merged_remotes: set[str] = set()
    if res_merged.returncode == 0:
        for line in res_merged.stdout.splitlines():
            ref = line.strip()
            if ref:
                merged_remotes.add(ref)

    # Todas as branches remotas
    res_all = run_git(["branch", "-r", "--format=%(refname:short)"], cwd=cwd)
    results: list[RemoteBranchInfo] = []

    if res_all.returncode == 0:
        for line in res_all.stdout.splitlines():
            full_ref = line.strip()
            if not full_ref or "->" in full_ref or full_ref.endswith("/HEAD"):
                continue

            if not full_ref.startswith(remote_prefix):
                continue

            branch_name = full_ref[len(remote_prefix) :]
            is_prot = is_protected_branch(branch_name)
            is_mrg = full_ref in merged_remotes

            results.append(
                RemoteBranchInfo(
                    name=branch_name,
                    full_ref=full_ref,
                    is_protected=is_prot,
                    is_merged=is_mrg,
                )
            )

    return sorted(results, key=lambda b: b.name)


def delete_local_branches(
    branch_names: list[str],
    dry_run: bool = False,
    cwd: Path | None = None,
) -> dict[str, tuple[bool, str]]:
    """Exclui com segurança as branches locais informadas.

    Nunca exclui a branch atual ou branches protegidas.
    """
    current_branch = get_current_branch(cwd)
    results: dict[str, tuple[bool, str]] = {}

    for name in branch_names:
        if name == current_branch:
            results[name] = (False, "Não é permitido excluir a branch atual (HEAD).")
            continue
        if is_protected_branch(name):
            results[name] = (False, f"Branch '{name}' é canônica/protegida.")
            continue

        if dry_run:
            results[name] = (True, "Simulado (--dry-run)")
            continue

        res = run_git(["branch", "-D", name], cwd=cwd)
        if res.returncode == 0:
            results[name] = (True, "")
        else:
            results[name] = (False, res.stderr.strip() or "Falha ao excluir branch.")

    return results


def delete_remote_branches(
    branch_names: list[str],
    remote: str = "origin",
    dry_run: bool = False,
    cwd: Path | None = None,
) -> dict[str, tuple[bool, str]]:
    """Exclui branches no repositório remoto informado (git push <remote> --delete <names>).

    Nunca permite a exclusão de branches canônicas/protegidas.
    """
    results: dict[str, tuple[bool, str]] = {}

    valid_targets: list[str] = []
    for name in branch_names:
        clean_name = name.replace(f"{remote}/", "").strip()
        if is_protected_branch(clean_name):
            results[clean_name] = (False, f"Branch '{clean_name}' é canônica/protegida.")
            continue
        valid_targets.append(clean_name)

    if not valid_targets:
        return results

    if dry_run:
        for name in valid_targets:
            results[name] = (True, f"Simulado: git push {remote} --delete {name}")
        return results

    # Executa a remoção remota
    res = run_git(["push", remote, "--delete", *valid_targets], cwd=cwd)
    if res.returncode == 0:
        for name in valid_targets:
            results[name] = (True, "")
    else:
        err_msg = res.stderr.strip() or "Erro ao excluir branches remotas."
        for name in valid_targets:
            results[name] = (False, err_msg)

    return results
