"""Planeja/aplica somente versão e changelog; publicação pertence ao workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASELINE = "e9f375fd2f11259fa5b7b9bd981363d91e7fcd5b"
VERSION_FILE = Path("src/utility_belt/__init__.py")
VERSION_PATTERN = re.compile(r'^__version__ = "(\d+\.\d+\.\d+)"$', re.MULTILINE)
COMMIT_PATTERN = re.compile(r"^(?P<type>[a-z]+)(?:\([^\n)]+\))?(?P<breaking>!)?: ")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()


def next_version(current: str, messages: list[str]) -> str | None:
    major, minor, patch = map(int, current.split("."))
    level = 0
    for message in messages:
        match = COMMIT_PATTERN.match(message)
        if not match:
            continue
        if match["breaking"] or re.search(r"^BREAKING[ -]CHANGE:", message, re.MULTILINE):
            level = max(level, 2 if major == 0 else 3)
        elif match["type"] == "feat":
            level = max(level, 2)
        elif match["type"] == "fix":
            level = max(level, 1)
    if level == 3:
        return f"{major + 1}.0.0"
    if level == 2:
        return f"{major}.{minor + 1}.0"
    if level == 1:
        return f"{major}.{minor}.{patch + 1}"
    return None


def plan_release(root: Path, *, baseline: str = BASELINE) -> dict:
    content = (root / VERSION_FILE).read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(content)
    if not match:
        raise ValueError("Fonte canônica de versão ausente ou inválida")
    current = match[1]
    current_tag = f"v{current}"
    tags = [tag for tag in git(root, "tag", "--merged", "HEAD", "--list", "v*").splitlines()
            if re.fullmatch(r"v\d+\.\d+\.\d+", tag)]
    if tags and current_tag not in tags:
        raise ValueError("Versão fonte diverge das tags; intervenção humana necessária")
    if any(tuple(map(int, tag[1:].split("."))) > tuple(map(int, current.split("."))) for tag in tags):
        raise ValueError("Há uma tag mais nova que a fonte; não retroceder versão")
    start = current_tag if current_tag in tags else baseline
    git(root, "merge-base", "--is-ancestor", start, "HEAD")
    if current_tag in tags:
        tagged = git(root, "show", f"{current_tag}:{VERSION_FILE.as_posix()}")
        if not VERSION_PATTERN.search(tagged) or VERSION_PATTERN.search(tagged)[1] != current:
            raise ValueError("Tag e fonte canônica não correspondem")
    messages = [message.strip() for message in git(
        root, "log", "--no-merges", "--format=%B%x1e", f"{start}..HEAD",
    ).split("\x1e") if message.strip()]
    version = next_version(current, messages)
    if not version:
        return {"changed": False, "version": current, "tag": current_tag if tags else "", "notes": ""}
    tag = f"v{version}"
    # Uma tag já publicada fora da ancestralidade também não pode ser sobrescrita.
    if tag in git(root, "tag", "--list", tag).splitlines():
        raise ValueError(f"Tag {tag} já existe; não sobrescrever")
    items = [f"- {message.splitlines()[0]}" for message in messages if COMMIT_PATTERN.match(message)]
    date = datetime.now(timezone.utc).date().isoformat()
    return {"changed": True, "version": version, "tag": tag,
            "notes": f"## {tag} ({date})\n\n" + "\n".join(items) + "\n"}


def apply_release(root: Path, plan: dict) -> None:
    if not plan["changed"]:
        return
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Checkout contém mudanças; release exige base limpa")
    path = root / VERSION_FILE
    content = path.read_text(encoding="utf-8")
    updated, count = VERSION_PATTERN.subn(f'__version__ = "{plan["version"]}"', content)
    if count != 1:
        raise ValueError("Fonte de versão ambígua")
    changelog = root / "CHANGELOG.md"
    previous = changelog.read_text(encoding="utf-8") if changelog.exists() else "# Changelog\n"
    body = previous.removeprefix("# Changelog").lstrip()
    path.write_text(updated, encoding="utf-8")
    changelog.write_text(f'# Changelog\n\n{plan["notes"]}\n{body}', encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--notes-file", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    plan = plan_release(root, baseline=args.baseline)
    if args.apply:
        apply_release(root, plan)
    if args.notes_file:
        args.notes_file.write_text(plan["notes"], encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
            for key in ("changed", "version", "tag"):
                stream.write(f"{key}={str(plan[key]).lower()}\n")
    print(json.dumps(plan, ensure_ascii=False))


if __name__ == "__main__":
    main()
