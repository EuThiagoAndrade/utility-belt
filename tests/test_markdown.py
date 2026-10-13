"""Contratos de integridade, configuração e consentimento sem rede externa."""

import hashlib
import io
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

from utility_belt import config, markdown
from utility_belt.markdown_runtime.runtime import RequirementError, Runtime


class FakeRuntime:
    def __init__(self, *, groups=(), audio=(), result=None):
        self.groups = groups
        self.audio = audio
        self.result = result or {"status": "success", "markdown": "---\ntitle: Teste\n---\n\nTexto\n"}
        self.calls = []

    def ensure(self, group, environment="core"):
        self.calls.append(("ensure", group, environment))

    def exiftool(self):
        self.calls.append(("exiftool",))
        return "exiftool"

    def worker(self, request, environment="core"):
        self.calls.append(("worker", request, environment))
        if request["action"] == "probe":
            return {"status": "ready", "groups": self.groups, "audio": self.audio,
                    "source_digest": hashlib.sha256(Path(request["source"]).read_bytes()).hexdigest()}
        return self.result


@pytest.fixture
def input_file(tmp_path):
    source = tmp_path / "relatório com espaços.pdf"
    source.write_bytes(b"known content")
    return source


def test_exclusive_concurrent_reservations(tmp_path):
    now = datetime(2026, 10, 12, 12, 30, 40)
    with ThreadPoolExecutor(max_workers=8) as pool:
        directories = list(pool.map(lambda _: markdown.reserve_operation(tmp_path, now=now), range(8)))
    assert len(set(directories)) == 8
    assert sorted(path.name for path in directories) == [
        "2026-10-12_12-30-40", *[f"2026-10-12_12-30-40_{i}" for i in range(2, 9)]
    ]


def test_publish_preserves_exact_engine_content_and_existing_file(tmp_path):
    content = "---\ntitle: Teste\n---\n\n\n  fim  \n"
    relative = Path("sub") / "arquivo.pdf.md"
    target = markdown.publish_markdown(tmp_path, relative, content)
    assert target.read_bytes() == content.encode("utf-8")
    with pytest.raises(FileExistsError):
        markdown.publish_markdown(tmp_path, relative, "replacement")
    assert target.read_bytes() == content.encode("utf-8")
    assert not list(tmp_path.rglob("*.tmp"))


@pytest.mark.parametrize("relative", [Path("../escape.md"), Path("/absolute.md")])
def test_reject_escape(tmp_path, relative):
    with pytest.raises(ValueError):
        markdown.publish_markdown(tmp_path, relative, "content")


def test_failed_publication_never_exposes_incomplete_file(tmp_path, monkeypatch):
    def interrupt(*_):
        raise KeyboardInterrupt
    monkeypatch.setattr(markdown.os, "link", interrupt)
    with pytest.raises(KeyboardInterrupt):
        markdown.publish_markdown(tmp_path, Path("result.md"), "full content")
    assert list(tmp_path.iterdir()) == []


def test_individual_name_and_no_incidental_config(input_file, tmp_path, monkeypatch):
    def unexpected(*_):
        pytest.fail("explicit output must not read or write preferences")
    monkeypatch.setattr(markdown, "load_markdown_output_dir", unexpected)
    result = markdown.convert(input_file, output_dir=tmp_path / "output", runtime=FakeRuntime())
    assert result.code == 0
    assert result.output.name == "relatório com espaços.pdf.md"
    assert result.output.read_text(encoding="utf-8").startswith("---\ntitle: Teste\n---")


@pytest.mark.parametrize("status,code", [("failed", 1), ("unsupported", 2), ("missing", 2)])
def test_engine_failure_retains_reserved_directory_without_markdown(input_file, tmp_path, status, code):
    runtime = FakeRuntime(result={"status": status, "markdown": "", "diagnostic": "failure"})
    result = markdown.convert(input_file, output_dir=tmp_path / "out", runtime=runtime)
    assert result.code == code
    assert result.output is None
    assert result.operation.is_dir()
    assert not list(result.operation.iterdir())


def test_zip_partial_publishes_content_and_reports_error(input_file, tmp_path):
    runtime = FakeRuntime(result={"status": "partial", "markdown": "known partial content",
                                 "failures": [{"member": "broken.pdf", "error": "parse failed"}]})
    result = markdown.convert(input_file, output_dir=tmp_path / "out", runtime=runtime)
    assert result.code == 1
    assert result.output.read_text() == "known partial content"
    assert "broken.pdf" in result.diagnostic


def test_preflight_rejects_invalid_input_without_motor(tmp_path):
    runtime = FakeRuntime()
    result = markdown.convert(tmp_path / "absent", output_dir=tmp_path / "out", runtime=runtime)
    assert result.code == 2 and result.operation is None
    assert not runtime.calls


def test_empty_input_never_acquires_motor(tmp_path):
    source = tmp_path / "empty"
    source.touch()
    runtime = FakeRuntime()
    result = markdown.convert(source, output_dir=tmp_path / "out", runtime=runtime)
    assert result.code == 2
    assert not runtime.calls


def test_missing_destination_never_prompts_or_installs(input_file, monkeypatch):
    monkeypatch.setattr(markdown, "load_markdown_output_dir", lambda: None)
    runtime = FakeRuntime()
    result = markdown.convert(input_file, runtime=runtime)
    assert result.code == 2 and not runtime.calls


def test_strict_config_preserves_document(tmp_path, monkeypatch):
    path = tmp_path / "config.toml"
    monkeypatch.setattr(config, "get_config_file", lambda: path)
    existing = config.get_default_config()
    existing["custom"] = {"number": 42}
    config.save_config(existing)
    output = config.save_markdown_output_dir(tmp_path / "new folder")
    document = tomllib.loads(path.read_text())
    assert document["profiles"] == existing["profiles"]
    assert document["custom"] == {"number": 42}
    assert config.load_markdown_output_dir() == output


def test_invalid_toml_never_overwritten(tmp_path, monkeypatch):
    path = tmp_path / "config.toml"
    path.write_bytes(b"invalid = [ TOML")
    monkeypatch.setattr(config, "get_config_file", lambda: path)
    with pytest.raises(tomllib.TOMLDecodeError):
        config.save_markdown_output_dir(tmp_path / "output")
    assert path.read_bytes() == b"invalid = [ TOML"
    assert list(tmp_path.iterdir()) == [path]


def test_no_tty_and_non_interactive_never_call_confirmation(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO())
    consent = markdown.Consent(confirm=lambda _: pytest.fail("must not prompt"))
    runtime = Runtime(consent, data_dir=tmp_path)
    source = tmp_path / "file.txt"
    source.write_text("text")
    result = markdown.convert(source, output_dir=tmp_path / "out", consent=consent, runtime=runtime)
    assert result.code == 2
    assert not runtime.root.exists()
    assert consent.audio([{"name": "sample.wav", "sha256": "abc"}]) == []
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    consent = markdown.Consent(non_interactive=True, confirm=lambda _: pytest.fail("must not prompt"))
    assert not consent.install("base", {"requirements": ["markitdown==0.1.8"], "purpose": "motor"})


def test_install_refusal_is_not_repeated_within_operation(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    calls = []
    consent = markdown.Consent(confirm=lambda message: calls.append(message) or False)
    recipe = {"requirements": ["markitdown[pdf]==0.1.8"], "purpose": "PDF"}
    assert not consent.install("pdf", recipe)
    assert not consent.install("pdf", recipe)
    assert len(calls) == 1


def test_audio_consent_is_separate_and_selects_audio_environment(input_file, tmp_path, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    prompts = []
    consent = markdown.Consent(confirm=lambda message: prompts.append(message) or True)
    runtime = FakeRuntime(audio=[{"name": "sample.wav", "sha256": "digest", "extension": ".wav"}])
    result = markdown.convert(input_file, output_dir=tmp_path / "out", runtime=runtime, consent=consent)
    assert result.code == 0
    assert "Google" in prompts[0] and "sample.wav" in prompts[0]
    requests = [entry for entry in runtime.calls if entry[0] == "worker"]
    assert requests[-1][1]["authorized_audio"] == ["digest"]
    assert requests[-1][2] == "audio"


@pytest.mark.parametrize("value", ["file:///etc/passwd", "https://user:secret@example.com", "https:///invalid"])
def test_invalid_url(value):
    with pytest.raises(ValueError):
        markdown.validate_url(value)


def test_changed_input_after_probe_is_rejected(input_file, tmp_path):
    class ChangedRuntime(FakeRuntime):
        def worker(self, request, environment="core"):
            result = super().worker(request, environment)
            input_file.write_bytes(b"changed")
            return result
    result = markdown.convert(input_file, output_dir=tmp_path / "out", runtime=ChangedRuntime())
    assert result.code == 2 and result.operation is None


@pytest.fixture
def http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "file:///etc/passwd")
            elif self.path == "/error":
                self.send_response(404)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Utility Belt fixture</h1>")

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


def test_http_snapshot_and_url_filename(http_server, tmp_path):
    runtime = FakeRuntime()
    result = markdown.convert(http_server, output_dir=tmp_path / "output", runtime=runtime)
    assert result.code == 0 and result.output.name == "web_content.md"
    probe = next(entry[1] for entry in runtime.calls if entry[0] == "worker")
    assert probe["stream_info"]["url"] == http_server
    assert probe["stream_info"]["mimetype"] == "text/html"
    assert not Path(probe["source"]).exists()  # temporários próprios liberados


@pytest.mark.parametrize("endpoint", ["/error", "/redirect"])
def test_http_failure_never_reserves_operation(http_server, tmp_path, endpoint):
    result = markdown.convert(http_server + endpoint, output_dir=tmp_path / "out", runtime=FakeRuntime())
    assert result.code == 2 and result.operation is None


def test_installer_is_never_called_before_consent(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    consent = markdown.Consent(confirm=lambda _: False)
    runtime = Runtime(consent, data_dir=tmp_path)
    monkeypatch.setattr("utility_belt.markdown_runtime.runtime.run_process", lambda *_: pytest.fail("installer called"))
    with pytest.raises(RequirementError, match="ausente"):
        runtime.ensure("pdf")
    assert not runtime.root.exists()


def test_acquisition_uses_only_packaged_recipe_and_explicit_interpreter(tmp_path, monkeypatch):
    import utility_belt.markdown_runtime.runtime as module
    consent_calls = []
    class Approve:
        def install(self, group, recipe):
            consent_calls.append((group, recipe))
            return True
    runtime = Runtime(Approve(), data_dir=tmp_path)
    observations = iter([False, True])
    monkeypatch.setattr(runtime, "available", lambda *_: next(observations))
    monkeypatch.setattr(module.shutil, "which", lambda _: "uv")
    commands = []
    def run(args, **kwargs):
        commands.append(args)
        return "uv 0.12.13" if args[-1] == "--version" else ""
    monkeypatch.setattr(module, "run_process", run)
    runtime.ensure("pdf")
    assert consent_calls[0][0] == "core:pdf"
    assert str(runtime.root / "core") in consent_calls[0][1]["purpose"]
    creation, installation = commands[-2:]
    assert "--no-python-downloads" in creation
    assert creation[creation.index("--python") + 1] == sys.executable
    assert "--no-config" in installation and "--require-hashes" in installation
    assert installation[installation.index("--python") + 1] == str(runtime.python())
    assert installation[installation.index("--requirements") + 1].endswith("pdf.txt")
    assert installation[installation.index("--constraints") + 1].endswith("constraints.txt")


def test_failed_install_requires_new_operation_consent_and_never_reports_available(tmp_path, monkeypatch):
    import utility_belt.markdown_runtime.runtime as module
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    messages = []
    consent = markdown.Consent(confirm=lambda message: messages.append(message) or True)
    runtime = Runtime(consent, data_dir=tmp_path)
    monkeypatch.setattr(runtime, "available", lambda *_: False)
    monkeypatch.setattr(module.shutil, "which", lambda _: "uv")
    def run(args, **kwargs):
        if args[-1] == "--version":
            return "uv 0.12.13"
        if "install" in args:
            raise RequirementError("Aquisição falhou")
        return ""
    monkeypatch.setattr(module, "run_process", run)
    with pytest.raises(RequirementError, match="Aquisição falhou"):
        runtime.ensure("pdf")
    assert len(messages) == 1
    second = Runtime(markdown.Consent(confirm=lambda message: messages.append(message) or False), data_dir=tmp_path)
    monkeypatch.setattr(second, "available", lambda *_: False)
    with pytest.raises(RequirementError, match="ausente"):
        second.ensure("pdf")
    assert len(messages) == 2


def test_core_never_acquires_transcription_libraries(tmp_path):
    runtime = Runtime(None, data_dir=tmp_path)
    with pytest.raises(RequirementError, match="somente"):
        runtime.ensure("audio-transcription", "core")
    assert not runtime.root.exists()


def test_cancelled_acquisition_preserves_prior_output(input_file, tmp_path):
    class CancelRuntime(FakeRuntime):
        def ensure(self, *_):
            raise KeyboardInterrupt
    destination = tmp_path / "out"
    destination.mkdir()
    existing = destination / "previous.md"
    existing.write_bytes(b"preserve")
    result = markdown.convert(input_file, output_dir=destination, runtime=CancelRuntime())
    assert result.code == 130 and result.operation is None
    assert existing.read_bytes() == b"preserve"


def test_existing_ffmpeg_is_reused_without_acquisition(tmp_path, monkeypatch):
    import utility_belt.markdown_runtime.runtime as module
    executable = tmp_path / "ffmpeg"
    runtime = Runtime(None, data_dir=tmp_path)
    monkeypatch.setattr(module.shutil, "which", lambda _: str(executable))
    monkeypatch.setattr(module, "run_process", lambda *_: "ffmpeg version test")
    monkeypatch.setattr(runtime, "ensure", lambda *_: pytest.fail("unexpected acquisition"))
    assert runtime.ffmpeg() == str(executable)


def test_missing_perl_never_downloads_exiftool(tmp_path, monkeypatch):
    from types import SimpleNamespace

    import utility_belt.markdown_runtime.runtime as module
    # Simula Linux sem instalar nenhum pacote de sistema.
    monkeypatch.setattr(module, "os", SimpleNamespace(name="posix"))
    monkeypatch.setattr(module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(module.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(module.shutil, "which", lambda _: None)
    class NoConsent:
        def install(self, *_):
            pytest.fail("must diagnose Perl before offering acquisition")
    runtime = Runtime(NoConsent(), data_dir=tmp_path)
    with pytest.raises(RequirementError, match="Perl"):
        runtime.exiftool()
    assert not runtime.root.exists()
