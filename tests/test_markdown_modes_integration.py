"""Integração real do Item 2 com ambientes previamente adquiridos (opt-in)."""

import os
import queue
import shutil
import sys
import threading
from pathlib import Path

import pytest

from utility_belt.markdown import batch, clipboard
from utility_belt.markdown_runtime.runtime import Runtime
from utility_belt.markdown_watch import watch

FIXTURES = Path(__file__).parent / "fixtures" / "markdown"


class NoDownloads:
    def install(self, *_):
        pytest.fail("Smoke não autoriza nova aquisição")
    def audio(self, *_):
        return []


@pytest.fixture
def runtime():
    data = os.environ.get("BELT_MARKDOWN_TEST_DATA")
    if not data:
        pytest.skip("BELT_MARKDOWN_TEST_DATA requer aquisições reais prévias")
    return Runtime(NoDownloads(), data_dir=data)


def test_native_recursive_batch_preserves_partial_output_and_audio_fallback(runtime, tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    for relative, name in [("a/report.pdf", "sample.pdf"), ("b/deep/report.docx", "sample.docx"),
                           ("b/deep/audio.wav", "sample.wav"), ("partial.zip", "partial.zip")]:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FIXTURES / name, target)
    result = batch(root, output_dir=root / "output", runtime=runtime, consent=NoDownloads(), non_interactive=True)
    assert (result.code, result.successes, result.failures) == (1, 3, 1)
    assert len(list((root / "output").iterdir())) == 1
    assert (result.operation / "b/deep/report.docx.md").is_file()
    assert "SampleRate: 16000" in (result.operation / "b/deep/audio.wav.md").read_text()
    assert "Transcript" not in (result.operation / "b/deep/audio.wav.md").read_text()
    assert "Utility Belt fixture" in (result.operation / "partial.zip.md").read_text()


def test_clipboard_native_file(runtime, tmp_path):
    result = clipboard(reader=lambda: f' "{FIXTURES / "sample.txt"}" ', output_dir=tmp_path,
                       runtime=runtime, consent=NoDownloads())
    assert result.code == 0 and "Utility Belt fixture" in result.output.read_text()


def test_watch_native_engine_and_real_observer(runtime, tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    ready, stop = threading.Event(), threading.Event()
    completed = queue.Queue()
    result = []
    thread = threading.Thread(target=lambda: result.append(watch(
        root, output_dir=root / "output", runtime=runtime, consent=NoDownloads(), non_interactive=True,
        stop_event=stop, on_ready=ready.set, on_result=lambda path, outcome: completed.put((path, outcome)))))
    thread.start()
    try:
        assert ready.wait(10)
        source = root / "new/deep/file.txt"
        source.parent.mkdir(parents=True)
        shutil.copyfile(FIXTURES / "sample.txt", source)
        observed, outcome = completed.get(timeout=30)
        assert observed == source and outcome.code == 0, outcome.diagnostic
        assert outcome.output.relative_to(outcome.operation) == Path("new/deep/file.txt.md")
        assert "Utility Belt fixture" in outcome.output.read_text()
    finally:
        stop.set()
        thread.join(timeout=10)
    assert not thread.is_alive() and result[0].successes == 1 and result[0].code == 130


def test_headless_linux_clipboard_reports_backend_absence():
    if sys.platform != "linux" or os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return  # ausência do backend é cenário específico da sessão headless
    result = clipboard()
    assert result.code == 2 and "Clipboard" in result.diagnostic
