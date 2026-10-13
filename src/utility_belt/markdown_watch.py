"""Monitor Markdown em primeiro plano, com um trabalhador e ciclos de vida."""

from __future__ import annotations

import queue
import time
from dataclasses import dataclass
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utility_belt.markdown import (
    Consent,
    ConversionResult,
    OperationResult,
    convert,
    eligible_path,
    enumerate_files,
    folder_roots,
    operation_summary,
)
from utility_belt.markdown_runtime.runtime import Runtime


def file_identity(path):
    metadata = path.stat()
    # ctime também distingue remoção/recriação quando o filesystem recicla inode.
    identity = (metadata.st_dev, metadata.st_ino, metadata.st_ctime_ns,
                metadata.st_size, metadata.st_mtime_ns)
    with path.open("rb") as stream:
        stream.read(1)
    return identity


@dataclass
class Pending:
    started: float
    next_check: float
    previous: tuple | None = None


class Monitor:
    """O observador somente enfileira eventos; estado e prompts vivem no trabalhador."""

    def __init__(self, root, destination, consent, runtime, *, clock=time.monotonic, converter=convert,
                 non_interactive=False):
        self.root = root
        self.destination = destination
        self.consent = consent
        self.runtime = runtime
        self.clock = clock
        self.converter = converter
        self.non_interactive = non_interactive
        self.events = queue.Queue()
        self.seen = set(enumerate_files(root, destination))
        self.pending = {}
        self.results = []
        self.ignored = 0
        self.notifications = []

    def add(self, path, started):
        path = Path(path).absolute()
        if path in self.seen or path in self.pending or not eligible_path(path, self.root, self.destination):
            return
        if path.is_file():
            self.pending[path] = Pending(started, started)

    def remove(self, path):
        for existing in list(self.seen):
            if existing == path or existing.is_relative_to(path):
                self.seen.remove(existing)
        for existing in list(self.pending):
            if existing == path or existing.is_relative_to(path):
                del self.pending[existing]

    def accept_event(self, kind, source, destination, is_directory, started):
        source = Path(source).absolute()
        if kind == "deleted":
            self.remove(source)
            return
        target = Path(destination).absolute() if kind == "moved" else source
        if kind == "moved":
            # Renomear estoque/arquivo concluído dentro da árvore não cria um
            # novo ciclo. Novos arquivos pendentes acompanham o caminho atual.
            for existing in list(self.seen):
                if existing == source or (is_directory and existing.is_relative_to(source)):
                    self.seen.remove(existing)
                    translated = target / existing.relative_to(source) if is_directory else target
                    if eligible_path(translated, self.root, self.destination):
                        self.seen.add(translated)
            for existing in list(self.pending):
                if existing == source or (is_directory and existing.is_relative_to(source)):
                    item = self.pending.pop(existing)
                    translated = target / existing.relative_to(source) if is_directory else target
                    if eligible_path(translated, self.root, self.destination):
                        item.previous = None
                        item.next_check = self.clock()
                        self.pending[translated] = item
        if is_directory:
            if eligible_path(target, self.root, self.destination) and target.is_dir():
                try:
                    paths = enumerate_files(self.root, self.destination, target)
                except OSError as exc:
                    result = ConversionResult(1, "failed", f"Não foi possível enumerar {target}: {exc}")
                    self.results.append(result)
                    self.notifications.append((target, result))
                    return
                for path in paths:
                    self.add(path, started)
        else:
            self.add(target, started)

    def drain_events(self):
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            self.accept_event(*event)

    def process_due(self):
        """Executa no máximo um candidato, para processar exclusões antes do próximo."""
        now = self.clock()
        for path, item in list(self.pending.items()):
            if now < item.next_check:
                continue
            if not eligible_path(path, self.root, self.destination):
                self.pending.pop(path)
                self.ignored += 1
                return None
            if now - item.started >= 30:
                result = ConversionResult(1, "failed", f"Timeout de estabilidade (30 s): {path}")
            else:
                try:
                    observed = file_identity(path)
                except OSError:
                    item.previous = None
                    item.next_check = now + 1
                    continue
                if observed != item.previous:
                    item.previous = observed
                    item.next_check = now + 1
                    continue

                def unchanged():
                    try:
                        return eligible_path(path, self.root, self.destination) and file_identity(path) == observed
                    except OSError:
                        return False

                # Revalidar imediatamente antes da conversão e antes de publicar.
                if not unchanged():
                    item.previous = None
                    item.next_check = now + 1
                    continue
                result = self.converter(path, output_dir=self.destination, consent=self.consent,
                                        runtime=self.runtime, non_interactive=self.non_interactive,
                                        _relative=Path(str(path.relative_to(self.root)) + ".md"),
                                        _before_publish=unchanged)
                # O hook do núcleo já revalidou após o motor e antes de publicar.
                # Uma edição após publicação é edição de arquivo concluído, não
                # motivo para esconder um resultado completo e reconvertê-lo.
                if result.code != 130 and result.output is None and not unchanged():
                    item.previous = None
                    item.next_check = self.clock() + 1
                    return None
            self.pending.pop(path)
            self.seen.add(path)
            if result.status == "unsupported":
                self.ignored += 1
            else:
                self.results.append(result)
            return path, result
        return None


class Handler(FileSystemEventHandler):
    def __init__(self, monitor):
        self.monitor = monitor

    def submit(self, kind, event):
        self.monitor.events.put((kind, event.src_path, getattr(event, "dest_path", ""),
                                 event.is_directory, self.monitor.clock()))

    def on_created(self, event):
        self.submit("created", event)

    def on_moved(self, event):
        self.submit("moved", event)

    def on_deleted(self, event):
        self.submit("deleted", event)


def watch(source, *, output_dir=None, non_interactive=False, consent=None, runtime=None,
          on_result=None, stop_event=None, on_ready=None):
    """Acompanha novos arquivos; Ctrl+C/stop_event encerra com 130 e libera observador."""
    observer = None
    monitor = None
    try:
        root, destination = folder_roots(source, output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        consent = consent or Consent(non_interactive=non_interactive)
        runtime = runtime or Runtime(consent)
        monitor = Monitor(root, destination, consent, runtime, non_interactive=non_interactive)
        observer = Observer()
        observer.schedule(Handler(monitor), str(root), recursive=True)
        observer.start()
        if on_ready:
            on_ready()
        while stop_event is None or not stop_event.is_set():
            monitor.drain_events()
            while monitor.notifications:
                path, result = monitor.notifications.pop(0)
                if on_result:
                    on_result(path, result)
            completed = monitor.process_due()
            if completed:
                path, result = completed
                if on_result:
                    on_result(path, result)
                if result.code == 130:
                    break
            try:
                event = monitor.events.get(timeout=0.1)
                monitor.accept_event(*event)
            except queue.Empty:
                pass
        return operation_summary(monitor.results, monitor.ignored, cancelled=True)
    except (KeyboardInterrupt, EOFError):
        return operation_summary(monitor.results if monitor else [], monitor.ignored if monitor else 0, cancelled=True)
    except (ValueError, OSError) as exc:
        previous = operation_summary(monitor.results if monitor else [], monitor.ignored if monitor else 0)
        return OperationResult(1 if previous.successes else 2, previous.successes, previous.failures + 1,
                               previous.ignored, previous.results, str(exc))
    finally:
        if observer is not None:
            observer.stop()
            if observer.is_alive():
                observer.join()
