"""Lote finito/recursivo, clipboard e consentimentos sem serviços externos."""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from utility_belt import markdown
from utility_belt.markdown_runtime import runtime as runtime_module


class Engine:
    def __init__(self):
        self.calls = []

    def ensure(self, *args):
        pass

    def worker(self, request, environment="core"):
        self.calls.append((request, environment))
        name = Path(request["source"]).name
        if request["action"] == "probe":
            sha = hashlib.sha256(Path(request["source"]).read_bytes()).hexdigest()
            audio = [{"name": name, "sha256": sha, "extension": ".wav"}] if name.endswith(".wav") else []
            return {"status": "ready", "source_digest": sha, "converters": [] if name.endswith(".unknown") else ["PlainTextConverter"],
                    "groups": ["pdf"] if name.endswith(".pdf") else [], "audio": audio}
        if name.startswith("bad"):
            return {"status": "failed", "diagnostic": "broken", "markdown": ""}
        return {"status": "success", "markdown": "Utility Belt fixture"}


def write(root, name, content="fixture"):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_batch_one_folder_relative_names_and_output_exclusion(tmp_path):
    root = tmp_path / "source"
    first = write(root, "level/report.pdf")
    write(root, "level/deeper/report.docx")
    write(root, "other/report.pdf")
    destination = root / "output"
    previous = write(destination, "old.md", "preserve")
    runtime = Engine()
    result = markdown.batch(root, output_dir=destination, runtime=runtime)
    assert result.code == 0 and result.successes == 3 and result.failures == 0
    assert sorted(str(path.relative_to(result.operation)).replace("\\", "/") for path in result.operation.rglob("*.md")) == [
        "level/deeper/report.docx.md", "level/report.pdf.md", "other/report.pdf.md"
    ]
    assert len([path for path in destination.iterdir() if path.is_dir()]) == 1
    assert previous.read_text() == "preserve"
    assert first.read_text() == "fixture"
    probes = [Path(request["source"]).relative_to(root).as_posix() for request, _ in runtime.calls if request["action"] == "probe"]
    assert probes == ["level/deeper/report.docx", "level/report.pdf", "other/report.pdf"]


def test_batch_partial_failure_and_ignored_do_not_remove_success(tmp_path):
    root = tmp_path / "source"
    write(root, "good.txt")
    write(root, "bad.txt")
    write(root, "ignored.unknown")
    result = markdown.batch(root, output_dir=tmp_path / "out", runtime=Engine())
    assert (result.code, result.successes, result.failures, result.ignored) == (1, 1, 1, 1)
    assert (result.operation / "good.txt.md").is_file()
    assert not (result.operation / "bad.txt.md").exists()


@pytest.mark.parametrize("kind", ["empty", "ignored", "failed", "same"])
def test_batch_terminal_codes(tmp_path, kind):
    root = tmp_path / "source"
    root.mkdir()
    if kind != "empty":
        write(root, "ignored.unknown" if kind == "ignored" else "bad.txt")
    output = root if kind == "same" else tmp_path / "out"
    result = markdown.batch(root, output_dir=output, runtime=Engine())
    assert result.code == (1 if kind == "failed" else 2)
    if kind in ("empty", "ignored", "same"):
        assert result.operation is None


def test_cancelled_batch_preserves_successful_results(tmp_path):
    root = tmp_path / "source"
    write(root, "a.txt")
    write(root, "b.txt")
    runtime = Engine()
    original = runtime.worker
    def worker(request, environment="core"):
        if request["action"] == "convert" and Path(request["source"]).name == "b.txt":
            raise KeyboardInterrupt
        return original(request, environment)
    runtime.worker = worker
    result = markdown.batch(root, output_dir=tmp_path / "out", runtime=runtime)
    assert result.code == 130 and result.successes == 1
    assert (result.operation / "a.txt.md").is_file()


def test_batch_asks_audio_once_for_finite_set(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    root = tmp_path / "source"
    write(root, "a.wav", "first")
    write(root, "b.wav", "second")
    messages = []
    consent = markdown.Consent(confirm=lambda message: messages.append(message) or True)
    runtime = Engine()
    result = markdown.batch(root, output_dir=tmp_path / "out", runtime=runtime, consent=consent)
    assert result.code == 0
    assert len(messages) == 1 and "a.wav" in messages[0] and "b.wav" in messages[0]
    requests = [request for request, environment in runtime.calls if request["action"] == "convert"]
    assert all(len(request["authorized_audio"]) == 1 for request in requests)
    assert requests[0]["authorized_audio"] != requests[1]["authorized_audio"]


def test_batch_non_interactive_never_sends_audio(tmp_path):
    root = tmp_path / "source"
    write(root, "sample.wav")
    class Forbidden:
        def audio(self, *_):
            pytest.fail("non-interactive audio prompt")
    runtime = Engine()
    result = markdown.batch(root, output_dir=tmp_path / "out", runtime=runtime, consent=Forbidden(), non_interactive=True)
    assert result.code == 0
    assert all(not request.get("authorized_audio") for request, _ in runtime.calls)


def test_changed_batch_input_after_consent_is_not_sent(tmp_path):
    root = tmp_path / "source"
    source = write(root, "sample.wav")
    class Changes:
        def audio(self, entries):
            source.write_text("changed audio")
            return [entry["sha256"] for entry in entries]
    runtime = Engine()
    result = markdown.batch(root, output_dir=tmp_path / "out", runtime=runtime, consent=Changes())
    assert result.code == 2
    assert all(request["action"] == "probe" for request, _ in runtime.calls)


def test_failed_acquisition_is_not_repeated_for_other_files(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    root = tmp_path / "source"
    for name in ["a.pdf", "b.pdf", "good.txt"]:
        write(root, name)
    messages, commands = [], []
    consent = markdown.Consent(confirm=lambda message: messages.append(message) or True)
    runtime = runtime_module.Runtime(consent, data_dir=tmp_path / "runtime")
    monkeypatch.setattr(runtime, "available", lambda group, *_: group == "base")
    engine = Engine()
    monkeypatch.setattr(runtime, "worker", engine.worker)
    monkeypatch.setattr(runtime_module.shutil, "which", lambda _: "uv")
    def run(args, **kwargs):
        commands.append(args)
        if "--version" in args:
            return "uv 0.12.13"
        if "install" in args:
            raise runtime_module.RequirementError("acquisition failed")
        return ""
    monkeypatch.setattr(runtime_module, "run_process", run)
    result = markdown.batch(root, output_dir=tmp_path / "out", runtime=runtime, consent=consent)
    assert (result.code, result.successes, result.failures) == (1, 1, 2)
    assert len(messages) == 1
    assert sum("install" in command for command in commands) == 1


@pytest.mark.parametrize("entry", ["", "   ", "free text", '""'])
def test_invalid_clipboard(entry, tmp_path):
    result = markdown.clipboard(reader=lambda: entry, output_dir=tmp_path, runtime=Engine())
    assert result.code == 2 and result.output is None


def test_quoted_clipboard_file_delegates_to_conversion(tmp_path):
    source = write(tmp_path, "source.txt")
    result = markdown.clipboard(reader=lambda: f'  "{source}"  ', output_dir=tmp_path / "out", runtime=Engine())
    assert result.code == 0 and result.output.name == "source.txt.md"


def test_clipboard_backend_failure_and_cancel(tmp_path):
    def unavailable():
        raise RuntimeError("backend missing")
    result = markdown.clipboard(reader=unavailable, output_dir=tmp_path)
    assert result.code == 2 and "backend missing" in result.diagnostic
    def cancelled():
        raise KeyboardInterrupt
    assert markdown.clipboard(reader=cancelled, output_dir=tmp_path).code == 130


def test_clipboard_default_backend_and_url_delegate(tmp_path, monkeypatch):
    import pyperclip
    monkeypatch.setattr(pyperclip, "paste", lambda: " https://example.com/fixture ")
    def snapshot(url, target):
        assert url == "https://example.com/fixture"
        target.write_text("<h1>Utility Belt fixture</h1>")
        return {"url": url, "mimetype": "text/html"}
    monkeypatch.setattr(markdown, "fetch_url", snapshot)
    result = markdown.clipboard(output_dir=tmp_path, runtime=Engine())
    assert result.code == 0 and result.output.name == "web_content.md"


def test_enumeration_does_not_follow_symlinks(tmp_path):
    root = tmp_path / "source"
    write(root, "own.txt")
    outside = tmp_path / "outside"
    write(outside, "private.txt")
    if os.name == "nt":
        for name, target in [("external", outside), ("cycle", root)]:
            command = subprocess.run(["cmd", "/c", "mklink", "/J", str(root / name), str(target)],
                                     capture_output=True)
            assert command.returncode == 0, command.stderr
    else:
        (root / "external").symlink_to(outside, target_is_directory=True)
        (root / "cycle").symlink_to(root, target_is_directory=True)
    assert markdown.enumerate_files(root, tmp_path / "out") == [root / "own.txt"]
