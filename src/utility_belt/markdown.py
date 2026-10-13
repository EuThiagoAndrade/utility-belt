"""Núcleo compartilhado de conversão Markdown e publicação segura de resultados."""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests

from utility_belt.config import load_markdown_output_dir
from utility_belt.markdown_runtime.runtime import RequirementError, Runtime


@dataclass(frozen=True)
class ConversionResult:
    code: int
    status: str
    diagnostic: str
    output: Path | None = None
    operation: Path | None = None


@dataclass(frozen=True)
class OperationResult:
    code: int
    successes: int
    failures: int
    ignored: int
    results: tuple[ConversionResult, ...]
    diagnostic: str = ""
    operation: Path | None = None


class Consent:
    """Consentimentos limitados a esta operação; padrão negativo e sem prompts em automação."""

    def __init__(self, *, non_interactive=False, confirm=None):
        self.interactive = not non_interactive and sys.stdin.isatty()
        self.confirm = confirm or self._ask
        self.decisions = {}

    @staticmethod
    def _ask(message):
        return input(f"{message} [s/N] ").strip().lower() in ("s", "sim")

    def install(self, group, recipe):
        if group in self.decisions:
            # Esta chamada só acontece se o requisito continua ausente. Uma
            # confirmação já consumida não autoriza repetir aquisição falha.
            return False
        if group not in self.decisions:
            message = f"Baixar e instalar {', '.join(recipe['requirements'])} e dependências necessárias para {recipe['purpose']} no diretório de dados do usuário?"
            if recipe.get("url"):
                message += f" Fonte: {recipe['url']}; SHA-256: {recipe['sha256']}."
            self.decisions[group] = self.interactive and bool(self.confirm(message))
        return self.decisions[group]

    def audio(self, entries):
        if not entries or not self.interactive:
            return []
        names = ", ".join(entry["name"] for entry in entries)
        if self.confirm(f"Enviar conteúdo de áudio ao serviço Google usado pelo MarkItDown, somente nesta operação: {names}?"):
            return [entry["sha256"] for entry in entries]
        return []


def validate_url(value):
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Informe arquivo existente ou URL HTTP(S) sem credenciais embutidas")
    return value


def reserve_operation(output_dir: Path, *, now=None):
    """mkdir exclusivo resolve colisões, inclusive entre processos simultâneos."""
    prefix = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    index = 1
    while True:
        candidate = output_dir / (prefix if index == 1 else f"{prefix}_{index}")
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            index += 1


def publish_markdown(operation: Path, relative: Path, text: str):
    """Publica arquivo completo usando hard link exclusivo, sem janela de sobrescrita."""
    if relative.is_absolute() or ".." in relative.parts or not relative.name:
        raise ValueError("Caminho de resultado inválido")
    target = operation / relative
    root = operation.resolve()
    if not target.resolve().is_relative_to(root):
        raise ValueError("Resultado escaparia da pasta da operação")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.parent.resolve().is_relative_to(root):
        raise ValueError("Pasta de resultado escaparia da operação")
    if not text.strip():
        raise ValueError("Conteúdo vazio não é conversão concluída")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=target.parent,
                                         prefix=".belt-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target


def fetch_url(url, target):
    """Baixa uma única representação HTTP; valida cada redirecionamento antes do acesso."""
    for _ in range(11):
        validate_url(url)
        with requests.get(url, allow_redirects=False, stream=True, timeout=(10, 30)) as response:
            if response.is_redirect or response.is_permanent_redirect:
                url = urljoin(url, response.headers["Location"])
                continue
            response.raise_for_status()
            with target.open("xb") as stream:
                for chunk in response.iter_content(65536):
                    stream.write(chunk)
            name = Path(unquote(urlsplit(url).path)).name
            return {"url": url, "filename": name or "web_content", "extension": Path(name).suffix or None,
                    "mimetype": response.headers.get("Content-Type", "").split(";")[0] or None}
    raise ValueError("URL excedeu o limite de redirecionamentos")


def convert(source: str | Path, *, output_dir=None, non_interactive=False, consent=None, runtime=None,
            _reserve=None, _relative=None, _probe=None, _authorized_audio=None, _before_publish=None):
    """Arquivo/URL individual; códigos 0/1/2/130 e nenhuma persistência incidental."""
    operation = None
    try:
        value = str(source)
        # Caminhos Windows com drive não são tratados como esquemas de URI.
        is_url = value.lower().startswith(("http:", "https:"))
        if is_url:
            validate_url(value)
            local = None
        else:
            local = Path(value).expanduser().resolve()
            if not local.is_file():
                raise ValueError(f"Entrada não é um arquivo existente: {value}")
            if not local.stat().st_size:
                raise ValueError("Entrada vazia não produz conversão")
        destination = Path(output_dir).expanduser().resolve() if output_dir is not None else load_markdown_output_dir()
        if destination is None:
            raise ValueError("Destino ausente; configure [markdown].output_dir ou informe output_dir")
        if destination.exists() and not destination.is_dir():
            raise ValueError(f"Destino não é uma pasta: {destination}")
        destination.mkdir(parents=True, exist_ok=True)
        consent = consent or Consent(non_interactive=non_interactive)
        runtime = runtime or Runtime(consent)
        runtime.ensure("base")
        with tempfile.TemporaryDirectory(prefix="belt-markdown-") as scratch:
            if is_url:
                path = Path(scratch) / "response"
                info = fetch_url(value, path)
                relative = Path("web_content.md")
            else:
                path = local
                info = {"filename": local.name, "extension": local.suffix, "local_path": str(local)}
                relative = Path(local.name + ".md")
            if path.stat().st_size == 0:
                raise ValueError("Entrada vazia não produz conversão")
            request = {"action": "probe", "source": str(path), "stream_info": info, "label": value}
            probe = _probe if _probe is not None else runtime.worker(request)
            if probe["status"] != "ready":
                return ConversionResult(1, "failed", probe.get("diagnostic", "Preflight do motor falhou"))
            authorized = [] if non_interactive else (
                _authorized_audio if _authorized_audio is not None else consent.audio(probe.get("audio", []))
            )
            environment = "audio" if authorized else "core"
            ffmpeg = None
            if environment == "audio":
                runtime.ensure("base", "audio")
                runtime.ensure("audio-transcription", "audio")
                if any(entry.get("extension") != ".wav" for entry in probe["audio"]):
                    ffmpeg = runtime.ffmpeg()
            exiftool = None
            for group in probe.get("groups", []):
                if group == "exiftool":
                    # Transcrição autorizada pode produzir texto sem metadados locais.
                    try:
                        exiftool = runtime.exiftool()
                    except RequirementError:
                        if not authorized:
                            raise
                else:
                    runtime.ensure(group, environment)
            expected = probe["source_digest"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError("Entrada mudou após preflight; repita a operação")
            operation = _reserve(destination) if _reserve else reserve_operation(destination)
            result = runtime.worker({**request, "action": "convert", "expected_digest": expected,
                                     "authorized_audio": authorized, "exiftool": exiftool, "ffmpeg": ffmpeg}, environment)
            # Detecção tardia de requisito conhecido permite uma única retomada, em processo novo.
            if result["status"] == "missing":
                for group in result.get("groups", []):
                    runtime.ensure(group, environment)
                result = runtime.worker({**request, "action": "convert", "expected_digest": expected,
                                         "authorized_audio": authorized, "exiftool": exiftool, "ffmpeg": ffmpeg}, environment)
            if result["status"] in ("success", "partial"):
                if _before_publish and not _before_publish():
                    return ConversionResult(1, "changed", "Entrada mudou durante conversão; resultado descartado",
                                            operation=operation)
                output = publish_markdown(operation, _relative or relative, result["markdown"])
                diagnostic = result.get("diagnostic", "")
                if result.get("failures"):
                    diagnostic += "; " + "; ".join(f"{entry['member']}: {entry['error']}" for entry in result["failures"])
                return ConversionResult(0 if result["status"] == "success" else 1,
                                        result["status"], diagnostic, output, operation)
            return ConversionResult(2 if result["status"] in ("unsupported", "missing") else 1,
                                    result["status"], result.get("diagnostic", "Conversão falhou"), operation=operation)
    except (KeyboardInterrupt, EOFError):
        return ConversionResult(130, "cancelled", "Operação cancelada; resultados anteriores preservados", operation=operation)
    except (ValueError, tomllib.TOMLDecodeError, RequirementError) as exc:
        return ConversionResult(2, "unavailable", str(exc), operation=operation)
    except (OSError, requests.RequestException, subprocess.TimeoutExpired) as exc:
        return ConversionResult(1 if operation else 2, "failed", str(exc), operation=operation)


def folder_roots(source, output_dir=None):
    root = Path(source).expanduser().resolve()
    destination = Path(output_dir).expanduser().resolve() if output_dir is not None else load_markdown_output_dir()
    if not root.is_dir():
        raise ValueError(f"Entrada não é uma pasta existente: {root}")
    if destination is None:
        raise ValueError("Destino ausente; configure [markdown].output_dir ou informe output_dir")
    if root == destination:
        raise ValueError("Raízes de entrada e saída não podem ser iguais")
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"Destino não é uma pasta: {destination}")
    return root, destination


def linked(path):
    try:
        metadata = path.lstat()
        return stat.S_ISLNK(metadata.st_mode) or bool(
            getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)
        )
    except OSError:
        return True


def eligible_path(path, root, destination):
    """Valida também os ancestrais: junctions podem surgir depois da enumeração."""
    path = Path(path).absolute()
    if not path.is_relative_to(root) or path == root:
        return False
    if path.resolve().is_relative_to(destination) or not path.resolve().is_relative_to(root):
        return False
    return not any(linked(part) for part in (path, *path.parents) if part.is_relative_to(root) and part != root)


def enumerate_files(root, destination, subtree=None):
    start = Path(subtree) if subtree is not None else root
    if start != root and not eligible_path(start, root, destination):
        return []
    paths = []
    def fail(error):
        raise error
    for directory, folders, files in os.walk(start, followlinks=False, onerror=fail):
        parent = Path(directory)
        folders[:] = sorted(name for name in folders if eligible_path(parent / name, root, destination))
        paths.extend(parent / name for name in sorted(files)
                     if eligible_path(parent / name, root, destination) and (parent / name).is_file())
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def batch(source, *, output_dir=None, non_interactive=False, consent=None, runtime=None, on_result=None):
    """Enumeração finita, consentimento de áudio pelo conjunto e pasta única."""
    results, ignored, operation = [], 0, None
    try:
        root, destination = folder_roots(source, output_dir)
        files = enumerate_files(root, destination)
        if not files:
            return OperationResult(2, 0, 0, 0, (), "Pasta sem arquivos elegíveis")
        consent = consent or Consent(non_interactive=non_interactive)
        runtime = runtime or Runtime(consent)
        runtime.ensure("base")
        prepared, entries = [], []
        for path in files:
            try:
                probe = runtime.worker({"action": "probe", "source": str(path), "label": str(path),
                                        "stream_info": {"filename": path.name, "extension": path.suffix,
                                                        "local_path": str(path)}})
            except (OSError, RequirementError, subprocess.TimeoutExpired) as exc:
                probe = {"status": "failed", "diagnostic": str(exc)}
            if probe["status"] == "ready" and probe.get("converters") == []:
                ignored += 1
                continue
            prepared.append((path, probe))
            entries.extend(probe.get("audio", []))
        authorized = set() if non_interactive else set(consent.audio(entries))

        def reserve(destination):
            nonlocal operation
            if operation is None:
                operation = reserve_operation(destination)
            return operation

        for path, probe in prepared:
            if not eligible_path(path, root, destination):
                result = ConversionResult(2, "unavailable", f"Entrada mudou ou tornou-se link: {path}")
            else:
                allowed = [entry["sha256"] for entry in probe.get("audio", []) if entry["sha256"] in authorized]
                result = convert(path, output_dir=destination, non_interactive=non_interactive,
                                 consent=consent, runtime=runtime, _reserve=reserve,
                                 _relative=Path(str(path.relative_to(root)) + ".md"), _probe=probe,
                                 _authorized_audio=allowed,
                                 _before_publish=lambda: eligible_path(path, root, destination))
            if result.status == "unsupported":
                ignored += 1
            else:
                results.append(result)
            if on_result:
                on_result(path, result)
            if result.code == 130:
                return operation_summary(results, ignored, operation, cancelled=True)
        return operation_summary(results, ignored, operation)
    except (KeyboardInterrupt, EOFError):
        return operation_summary(results, ignored, operation, cancelled=True)
    except (ValueError, OSError, RequirementError, subprocess.TimeoutExpired) as exc:
        return OperationResult(2, 0, 1, ignored, tuple(results), str(exc), operation)


def operation_summary(results, ignored=0, operation=None, *, cancelled=False):
    successes = sum(result.code == 0 for result in results)
    failures = sum(result.code not in (0, 130) for result in results)
    if cancelled:
        code = 130
    elif failures:
        code = 2 if not successes and all(result.code == 2 for result in results) else 1
    else:
        code = 0 if successes else 2
    return OperationResult(code, successes, failures, ignored, tuple(results),
                           f"Sucessos: {successes}; falhas: {failures}; ignorados: {ignored}", operation)


def clipboard(*, output_dir=None, non_interactive=False, consent=None, runtime=None, reader=None):
    try:
        if reader is None:
            import pyperclip
            reader = pyperclip.paste
        value = reader()
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Clipboard vazio ou sem entrada textual")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1].strip()
        if not value:
            raise ValueError("Clipboard vazio")
    except (KeyboardInterrupt, EOFError):
        return ConversionResult(130, "cancelled", "Leitura do clipboard cancelada")
    except Exception as exc:
        return ConversionResult(2, "unavailable", f"Clipboard indisponível ou inválido: {exc}")
    return convert(value, output_dir=output_dir, non_interactive=non_interactive, consent=consent, runtime=runtime)
