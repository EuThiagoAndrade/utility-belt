"""Versionamento e reexecuções validados em Git local, sem publicação."""

import importlib.util
import subprocess
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("belt_release", Path(__file__).parents[1] / "scripts/release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.mark.parametrize("current,messages,expected", [
    ("0.1.0", ["fix(issue-2): corrigir saída"], "0.1.1"),
    ("0.1.1", ["feat(issue-3): menu novo", "fix(issue-4): aviso"], "0.2.0"),
    ("0.2.0", ["feat!: alterar comandos"], "0.3.0"),
    ("1.2.3", ["feat!: alterar comandos"], "2.0.0"),
    ("1.2.3", ["refactor: comandos\n\nBREAKING CHANGE: remover argumento"], "2.0.0"),
    ("0.1.0", ["docs(cycle-007): plano", "chore: formatter"], None),
    ("0.1.0", ["Merge pull request #7", "mensagem sem convenção"], None),
    ("0.1.0", ["fix: primeira correção", "fix: segunda correção"], "0.1.1"),
])
def test_conventional_increment(current, messages, expected):
    assert release.next_version(current, messages) == expected


def commit(root, message):
    release.git(root, "add", ".")
    release.git(root, "commit", "--allow-empty", "-m", message)
    return release.git(root, "rev-parse", "HEAD")


@pytest.fixture
def repository(tmp_path):
    release.git(tmp_path, "init")
    release.git(tmp_path, "config", "user.name", "Release test")
    release.git(tmp_path, "config", "user.email", "release@example.invalid")
    path = tmp_path / release.VERSION_FILE
    path.parent.mkdir(parents=True)
    path.write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    baseline = commit(tmp_path, "feat: histórico anterior")
    return tmp_path, baseline


def test_bootstrap_ignores_history_and_docs(repository):
    root, baseline = repository
    commit(root, "docs: explicar menu")
    plan = release.plan_release(root, baseline=baseline)
    assert plan == {"changed": False, "version": "0.1.0", "tag": "", "notes": ""}


def test_apply_tag_and_retry_then_fix(repository):
    root, baseline = repository
    commit(root, "feat(issue-23): modernizar interface")
    first = release.plan_release(root, baseline=baseline)
    assert first["version"] == "0.2.0"
    release.apply_release(root, first)
    assert '"0.2.0"' in (root / release.VERSION_FILE).read_text()
    assert "feat(issue-23): modernizar interface" in (root / "CHANGELOG.md").read_text(encoding="utf-8")
    commit(root, "chore(release): v0.2.0")
    release.git(root, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    # Recupera uma GitHub Release ainda ausente sem incrementar/taggear outra vez.
    retry = release.plan_release(root, baseline=baseline)
    assert not retry["changed"] and retry["tag"] == "v0.2.0"
    commit(root, "fix(issue-24): corrigir mensagem")
    second = release.plan_release(root, baseline=baseline)
    assert second["version"] == "0.2.1"
    assert "modernizar" not in second["notes"]
    release.apply_release(root, second)
    assert "v0.2.0" in (root / "CHANGELOG.md").read_text(encoding="utf-8")


def test_dirty_checkout_cannot_apply_release(repository):
    root, baseline = repository
    commit(root, "fix: texto")
    plan = release.plan_release(root, baseline=baseline)
    (root / release.VERSION_FILE).write_text('__version__ = "0.1.0"\n# alheio\n')
    with pytest.raises(ValueError, match="mudanças"):
        release.apply_release(root, plan)
    assert not (root / "CHANGELOG.md").exists()


def test_inconsistent_tag_refuses_mutation(repository):
    root, baseline = repository
    release.git(root, "tag", "v0.2.0")
    with pytest.raises(ValueError, match="diverge"):
        release.plan_release(root, baseline=baseline)


def test_tag_contents_must_match_version(repository):
    root, baseline = repository
    release.git(root, "tag", "v0.2.0")
    (root / release.VERSION_FILE).write_text('__version__ = "0.2.0"\n')
    commit(root, "chore: fonte incorreta")
    with pytest.raises(ValueError, match="não correspondem"):
        release.plan_release(root, baseline=baseline)


def test_non_ancestor_baseline_is_rejected(repository):
    root, _ = repository
    with pytest.raises(subprocess.CalledProcessError):
        release.plan_release(root, baseline="deadbeef")
