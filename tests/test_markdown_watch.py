"""Estado, estabilidade e lifecycle do monitor; observador real em teste separado."""

import queue
import threading
import time
from pathlib import Path

import pytest

from utility_belt import markdown_watch
from utility_belt.markdown import ConversionResult


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def file(root, name, value="fixture"):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)
    return path


@pytest.fixture
def controlled(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    clock = Clock()
    calls = []
    def converter(path, **kwargs):
        calls.append((path, kwargs))
        assert kwargs["_before_publish"]()
        return ConversionResult(0, "success", "")
    monitor = markdown_watch.Monitor(root, root / "output", None, None, clock=clock, converter=converter)
    return monitor, clock, calls


def stabilize(monitor, clock):
    monitor.process_due()
    clock.now += 1
    return monitor.process_due()


def test_new_stable_file_deduplicates_and_preserves_relative_path(controlled):
    monitor, clock, calls = controlled
    path = file(monitor.root, "level/deeper/file.txt")
    monitor.add(path, 0)
    monitor.add(path, 0)
    assert stabilize(monitor, clock)[1].code == 0
    assert len(calls) == 1
    assert calls[0][1]["_relative"] == Path("level/deeper/file.txt.md")
    path.write_text("edited")
    monitor.add(path, clock.now)
    clock.now += 5
    assert monitor.process_due() is None and len(calls) == 1


def test_stock_never_converts_and_internal_moves_keep_lifecycle(tmp_path):
    root = tmp_path / "root"
    source = file(root, "stock.txt")
    monitor = markdown_watch.Monitor(root, tmp_path / "out", None, None, converter=lambda *_: pytest.fail("stock converted"))
    monitor.add(source, 0)
    destination = root / "renamed.txt"
    source.rename(destination)
    monitor.accept_event("moved", str(source), str(destination), False, 0)
    assert destination in monitor.seen and not monitor.pending


def test_delete_and_recreate_starts_new_lifecycle(controlled):
    monitor, clock, calls = controlled
    path = file(monitor.root, "file.txt")
    monitor.add(path, 0)
    stabilize(monitor, clock)
    path.unlink()
    monitor.accept_event("deleted", str(path), "", False, clock.now)
    file(monitor.root, "file.txt", "new lifecycle")
    monitor.add(path, clock.now)
    stabilize(monitor, clock)
    assert len(calls) == 2


def test_moved_directory_includes_files_in_new_nested_directories(controlled, tmp_path):
    monitor, clock, calls = controlled
    outside = tmp_path / "outside"
    file(outside, "deep/file.txt")
    destination = monitor.root / "new-folder"
    outside.rename(destination)
    monitor.accept_event("moved", str(outside), str(destination), True, 0)
    assert destination / "deep/file.txt" in monitor.pending
    stabilize(monitor, clock)
    assert len(calls) == 1


def test_slow_copy_waits_for_two_identical_observations(controlled):
    monitor, clock, calls = controlled
    path = file(monitor.root, "slow.txt", "a")
    monitor.add(path, 0)
    monitor.process_due()
    clock.now = 1
    path.write_text("longer")
    assert monitor.process_due() is None
    clock.now = 1.5
    assert monitor.process_due() is None
    clock.now = 2
    assert monitor.process_due()[1].code == 0
    assert len(calls) == 1


def test_timeout_and_read_failure_do_not_loop(controlled, monkeypatch):
    monitor, clock, calls = controlled
    path = file(monitor.root, "unreadable.txt")
    def unreadable(_):
        raise PermissionError("locked file")
    monkeypatch.setattr(markdown_watch, "file_identity", unreadable)
    monitor.add(path, 0)
    assert monitor.process_due() is None
    clock.now = 30
    result = monitor.process_due()
    assert result[1].code == 1 and "Timeout" in result[1].diagnostic
    clock.now = 60
    assert monitor.process_due() is None and not calls


def test_changed_during_conversion_restarts_stability_with_original_deadline(controlled):
    monitor, clock, calls = controlled
    path = file(monitor.root, "change.txt")
    original = monitor.converter
    def changes(path, **kwargs):
        path.write_text("changed during conversion")
        assert not kwargs["_before_publish"]()
        monitor.converter = original
        return ConversionResult(1, "changed", "discarded")
    monitor.converter = changes
    monitor.add(path, 0)
    assert stabilize(monitor, clock) is None
    assert monitor.pending[path].started == 0 and not monitor.results
    clock.now += 1
    monitor.process_due()
    clock.now += 1
    assert monitor.process_due()[1].code == 0
    assert len(calls) == 1


def test_output_tree_is_never_pending(controlled):
    monitor, clock, calls = controlled
    output = file(monitor.destination, "created/result.md")
    monitor.accept_event("created", str(monitor.destination), "", True, 0)
    monitor.add(output, 0)
    clock.now = 10
    assert monitor.process_due() is None and not monitor.pending and not calls


def test_monitor_passes_non_interactive_mode(controlled):
    monitor, clock, calls = controlled
    monitor.non_interactive = True
    monitor.add(file(monitor.root, "file.txt"), 0)
    stabilize(monitor, clock)
    assert calls[0][1]["non_interactive"] is True


def test_failure_does_not_stop_other_candidates(controlled):
    monitor, clock, calls = controlled
    first = file(monitor.root, "bad.txt")
    second = file(monitor.root, "good.txt")
    original = monitor.converter
    monitor.converter = lambda path, **kwargs: ConversionResult(1, "failed", "failure") if path == first else original(path, **kwargs)
    monitor.add(first, 0)
    monitor.add(second, 0)
    monitor.process_due()
    clock.now = 1
    assert monitor.process_due()[1].code == 1
    assert monitor.process_due()[1].code == 0
    assert len(monitor.results) == 2


def test_directory_read_failure_does_not_stop_monitor(controlled, monkeypatch):
    monitor, clock, calls = controlled
    directory = monitor.root / "unreadable"
    directory.mkdir()
    def unavailable(*_):
        raise PermissionError("directory locked")
    monkeypatch.setattr(markdown_watch, "enumerate_files", unavailable)
    monitor.accept_event("created", str(directory), "", True, 0)
    assert monitor.results[0].code == 1 and monitor.notifications[0][0] == directory
    monitor.add(file(monitor.root, "other.txt"), 0)
    assert stabilize(monitor, clock)[1].code == 0


def test_cancel_stops_and_joins_observer(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    calls = []
    class Observer:
        def schedule(self, *args, **kwargs):
            calls.append("schedule")
        def start(self):
            calls.append("start")
        def stop(self):
            calls.append("stop")
        def is_alive(self):
            return True
        def join(self):
            calls.append("join")
    monkeypatch.setattr(markdown_watch, "Observer", Observer)
    def cancel():
        raise KeyboardInterrupt
    result = markdown_watch.watch(root, output_dir=tmp_path / "out", on_ready=cancel)
    assert result.code == 130
    assert calls == ["schedule", "start", "stop", "join"]


def test_real_observer_recursion_moves_lifecycle_and_output_exclusion(tmp_path, monkeypatch):
    """Watchdog real com conversor local controlado, sem rede/downloads."""
    root = tmp_path / "root"
    root.mkdir()
    stock = file(root, "stock.txt")
    ready, stop = threading.Event(), threading.Event()
    completed = queue.Queue()
    outcomes = []
    errors = []
    def converter(path, **kwargs):
        assert kwargs["_before_publish"]()
        from utility_belt.markdown import publish_markdown, reserve_operation
        kwargs["output_dir"].mkdir(exist_ok=True)
        operation = reserve_operation(kwargs["output_dir"])
        target = publish_markdown(operation, kwargs["_relative"], path.read_text())
        return ConversionResult(0, "success", "", target, operation)
    # Só substituir o motor; observação e publicação/exclusão são reais.
    original = markdown_watch.Monitor
    def monitor(*args, **kwargs):
        return original(*args, **kwargs, converter=converter)
    monkeypatch.setattr(markdown_watch, "Monitor", monitor)
    def run():
        try:
            outcomes.append(markdown_watch.watch(root, output_dir=root / "output", on_ready=ready.set,
                                                 stop_event=stop, on_result=lambda path, result: completed.put((path, result))))
        except BaseException as exc:
            errors.append(exc)
    thread = threading.Thread(target=run)
    thread.start()
    try:
        assert ready.wait(10)
        stock.write_text("edit stock")
        new = file(root, "level/deeper/new.txt")
        path, result = completed.get(timeout=10)
        assert path == new and result.output.relative_to(result.operation) == Path("level/deeper/new.txt.md")
        new.write_text("edit completed")
        outside = tmp_path / "incoming"
        file(outside, "more/deep/moved.txt")
        outside.rename(root / "moved-folder")
        path, _ = completed.get(timeout=10)
        assert path == root / "moved-folder/more/deep/moved.txt"
        new.unlink()
        time.sleep(0.2)  # permitir evento real de exclusão antes de nova criação
        file(root, "level/deeper/new.txt", "recreated")
        path, _ = completed.get(timeout=10)
        assert path == new
        slow = root / "slow.txt"
        with slow.open("w") as stream:
            stream.write("slow-")
            stream.flush()
            time.sleep(0.4)
            stream.write("copy-")
            stream.flush()
            time.sleep(0.4)
            stream.write("complete")
        path, result = completed.get(timeout=10)
        assert path == slow and result.output.read_text() == "slow-copy-complete"
        time.sleep(1.2)
        assert completed.empty()  # nenhuma edição/estoque/saída realimentada
    finally:
        stop.set()
        thread.join(timeout=10)
    assert not thread.is_alive() and not errors
    assert outcomes[0].code == 130 and outcomes[0].successes == 4


def test_real_observer_stability_timeout_continues_after_unreadable_file(tmp_path, monkeypatch):
    root = tmp_path / "source"
    root.mkdir()
    original = markdown_watch.file_identity
    def identity(path):
        if path.name == "locked.txt":
            raise PermissionError("simulated unavailable reader")
        return original(path)
    monkeypatch.setattr(markdown_watch, "file_identity", identity)
    ready, stop = threading.Event(), threading.Event()
    completed = queue.Queue()
    results = []
    thread = threading.Thread(target=lambda: results.append(markdown_watch.watch(
        root, output_dir=tmp_path / "out", on_ready=ready.set, stop_event=stop,
        on_result=lambda path, result: completed.put((path, result)))))
    thread.start()
    try:
        assert ready.wait(10)
        path = file(root, "locked.txt")
        started = time.monotonic()
        observed, result = completed.get(timeout=35)
        assert observed == path and result.code == 1 and "Timeout" in result.diagnostic
        assert time.monotonic() - started >= 29.8
    finally:
        stop.set()
        thread.join(timeout=10)
    assert not thread.is_alive() and results[0].code == 130 and results[0].failures == 1
