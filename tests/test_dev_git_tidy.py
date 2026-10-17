"""Testes para o utilitário Git-Tidy (higienização de branches locais e remotas)."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

from utility_belt.dev.git_tidy import (
    LocalBranchInfo,
    RemoteBranchInfo,
    delete_local_branches,
    delete_remote_branches,
    get_local_branches,
    get_remote_branches,
    is_protected_branch,
)


def test_is_protected_branch() -> None:
    assert is_protected_branch("main") is True
    assert is_protected_branch("master") is True
    assert is_protected_branch("dev") is True
    assert is_protected_branch("develop") is True
    assert is_protected_branch("staging") is True
    assert is_protected_branch("production") is True
    assert is_protected_branch("origin/main") is True
    assert is_protected_branch("release/v1.0") is True
    assert is_protected_branch("v0.3.0") is True

    # Branches de trabalho não protegidas
    assert is_protected_branch("feature/issue-29") is False
    assert is_protected_branch("fix/bug-login") is False
    assert is_protected_branch("chore/cycle-009") is False


def test_local_branch_info_eligibility() -> None:
    # Branch atual nunca é elegível
    b1 = LocalBranchInfo("feat", is_current=True, is_protected=False, is_merged=True, is_gone=True)
    assert b1.is_eligible_for_deletion is False
    assert b1.status_label == "[Atual / HEAD]"

    # Branch protegida nunca é elegível
    b2 = LocalBranchInfo("main", is_current=False, is_protected=True, is_merged=True, is_gone=False)
    assert b2.is_eligible_for_deletion is False
    assert b2.status_label == "[Protegida]"

    # Branch mergeada é elegível
    b3 = LocalBranchInfo("fix/1", is_current=False, is_protected=False, is_merged=True, is_gone=False)
    assert b3.is_eligible_for_deletion is True
    assert b3.status_label == "[Mergeada]"

    # Branch gone (upstream removido / squash) é elegível
    b4 = LocalBranchInfo("feat/squash", is_current=False, is_protected=False, is_merged=False, is_gone=True)
    assert b4.is_eligible_for_deletion is True
    assert b4.status_label == "[Remoto removido / Squash]"

    # Branch com trabalho pendente não é elegível
    b5 = LocalBranchInfo("spike/wip", is_current=False, is_protected=False, is_merged=False, is_gone=False)
    assert b5.is_eligible_for_deletion is False
    assert b5.status_label == "[Trabalho pendente]"


def test_remote_branch_info_eligibility() -> None:
    # Remota protegida
    r1 = RemoteBranchInfo(name="main", full_ref="origin/main", is_protected=True, is_merged=True)
    assert r1.is_eligible_for_deletion is False
    assert r1.status_label == "[Protegida]"

    # Remota mergeada
    r2 = RemoteBranchInfo(name="feat/old", full_ref="origin/feat/old", is_protected=False, is_merged=True)
    assert r2.is_eligible_for_deletion is True
    assert r2.status_label == "[Mergeada no remote]"

    # Remota ativa
    r3 = RemoteBranchInfo(name="feat/wip", full_ref="origin/feat/wip", is_protected=False, is_merged=False)
    assert r3.is_eligible_for_deletion is False
    assert r3.status_label == "[Ativa / Não mergeada]"


def test_get_local_branches_mocked() -> None:
    def fake_run_git(args: list[str], cwd=None) -> subprocess.CompletedProcess[str]:
        if "rev-parse" in args and "--is-inside-work-tree" in args:
            return subprocess.CompletedProcess(args, 0, stdout="true\n")
        if "rev-parse" in args and "HEAD" in args:
            return subprocess.CompletedProcess(args, 0, stdout="main\n")
        if "symbolic-ref" in args:
            return subprocess.CompletedProcess(args, 0, stdout="refs/remotes/origin/main\n")
        if "branch" in args and "--merged" in args:
            return subprocess.CompletedProcess(args, 0, stdout="  main\n  feat/merged-pr\n")
        if "for-each-ref" in args and "--format=%(refname:short)|%(upstream:track)" in args:
            return subprocess.CompletedProcess(
                args, 0, stdout="feat/gone-pr|[gone]\nmain|\nfeat/wip|\n"
            )
        if "for-each-ref" in args and "--format=%(refname:short)" in args:
            return subprocess.CompletedProcess(
                args, 0, stdout="main\nfeat/merged-pr\nfeat/gone-pr\nfeat/wip\n"
            )
        return subprocess.CompletedProcess(args, 0, stdout="")

    with patch("utility_belt.dev.git_tidy.is_git_installed", return_value=True):
        with patch("utility_belt.dev.git_tidy.run_git", side_effect=fake_run_git):
            branches = get_local_branches()
            b_dict = {b.name: b for b in branches}

            assert "main" in b_dict
            assert b_dict["main"].is_current is True
            assert b_dict["main"].is_eligible_for_deletion is False

            assert "feat/merged-pr" in b_dict
            assert b_dict["feat/merged-pr"].is_merged is True
            assert b_dict["feat/merged-pr"].is_eligible_for_deletion is True

            assert "feat/gone-pr" in b_dict
            assert b_dict["feat/gone-pr"].is_gone is True
            assert b_dict["feat/gone-pr"].is_eligible_for_deletion is True

            assert "feat/wip" in b_dict
            assert b_dict["feat/wip"].is_eligible_for_deletion is False


def test_get_remote_branches_mocked() -> None:
    def fake_run_git(args: list[str], cwd=None) -> subprocess.CompletedProcess[str]:
        if "rev-parse" in args and "--is-inside-work-tree" in args:
            return subprocess.CompletedProcess(args, 0, stdout="true\n")
        if "symbolic-ref" in args:
            return subprocess.CompletedProcess(args, 0, stdout="refs/remotes/origin/main\n")
        if "branch" in args and "-r" in args and "--merged" in args:
            return subprocess.CompletedProcess(args, 0, stdout="  origin/main\n  origin/feat/pr-closed\n")
        if "branch" in args and "-r" in args:
            return subprocess.CompletedProcess(
                args, 0, stdout="origin/HEAD -> origin/main\norigin/main\norigin/feat/pr-closed\norigin/feat/active\n"
            )
        return subprocess.CompletedProcess(args, 0, stdout="")

    with patch("utility_belt.dev.git_tidy.is_git_installed", return_value=True):
        with patch("utility_belt.dev.git_tidy.run_git", side_effect=fake_run_git):
            remotes = get_remote_branches()
            r_dict = {r.name: r for r in remotes}

            assert "main" in r_dict
            assert r_dict["main"].is_protected is True
            assert r_dict["main"].is_eligible_for_deletion is False

            assert "feat/pr-closed" in r_dict
            assert r_dict["feat/pr-closed"].is_merged is True
            assert r_dict["feat/pr-closed"].is_eligible_for_deletion is True

            assert "feat/active" in r_dict
            assert r_dict["feat/active"].is_merged is False
            assert r_dict["feat/active"].is_eligible_for_deletion is False


def test_delete_local_branches_safety() -> None:
    with patch("utility_belt.dev.git_tidy.get_current_branch", return_value="main"):
        # Tentativa de deletar HEAD
        res = delete_local_branches(["main"])
        assert res["main"][0] is False
        assert "HEAD" in res["main"][1]

        # Tentativa de deletar branch protegida
        res = delete_local_branches(["master", "develop"])
        assert res["master"][0] is False
        assert res["develop"][0] is False

        # Modo dry-run em branch elegível
        res = delete_local_branches(["feature/old"], dry_run=True)
        assert res["feature/old"][0] is True
        assert "dry-run" in res["feature/old"][1]


def test_delete_remote_branches_safety() -> None:
    # Tentativa de deletar branch remota protegida
    res = delete_remote_branches(["origin/main", "origin/master", "origin/release/1.0"])
    assert res["main"][0] is False
    assert res["master"][0] is False
    assert res["release/1.0"][0] is False

    # Modo dry-run em branch remota elegível
    res = delete_remote_branches(["origin/feature/done"], dry_run=True)
    assert res["feature/done"][0] is True
    assert "Simulado" in res["feature/done"][1]
