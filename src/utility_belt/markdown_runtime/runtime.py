"""Aquisição restrita de receitas aprovadas, sem alterar o Python do Belt."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import zipfile
from pathlib import Path

import requests

from utility_belt.config import get_data_dir

RESOURCES = Path(__file__).parent
RECIPES = tomllib.loads((RESOURCES / "recipes.toml").read_text(encoding="utf-8"))


def recipe_revision():
    """Receitas incompatíveis nunca alteram um ambiente adquirido anteriormente."""
    digest = hashlib.sha256()
    for resource in sorted([RESOURCES / "recipes.toml", *RESOURCES.glob("*.txt")]):
        digest.update(resource.name.encode("utf-8"))
        digest.update(resource.read_bytes())
    return digest.hexdigest()[:16]


class RequirementError(Exception):
    """Requisito indisponível, recusado ou incompatível (código 2)."""


class AcquisitionError(RequirementError):
    """Aquisição consentida que falhou (código 1)."""


@contextlib.contextmanager
def environment_lock(root: Path, timeout=300):
    """Lock do sistema operacional; liberação automática inclusive após crash."""
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".lock").open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                stream.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RequirementError("Outro processo usa o motor; timeout de 300 segundos")
                time.sleep(0.1)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def run_process(args, **kwargs):
    """Mantém timeout e cancelamento sem processo órfão escrevendo na venv."""
    with subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, encoding="utf-8", errors="replace", **kwargs) as process:
        try:
            stdout, stderr = process.communicate(timeout=300)
        except BaseException:
            process.kill()
            process.communicate()
            raise
        if process.returncode:
            raise RequirementError(f"Processo falhou ({process.returncode}): {stderr.strip()}")
        return stdout


class Runtime:
    def __init__(self, consent, data_dir=None):
        self.consent = consent
        self.root = (Path(data_dir) if data_dir else get_data_dir()) / "markdown" / "engines" / "markitdown-0.1.8" / f"py{sys.version_info.major}.{sys.version_info.minor}" / f"recipes-{recipe_revision()}"

    def python(self, environment="core"):
        return self.root / environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    def available(self, group, environment="core"):
        interpreter = self.python(environment)
        if not interpreter.is_file():
            return False
        imports = RECIPES["groups"][group]["imports"]
        script = (
            "import importlib,importlib.metadata,importlib.util;"
            "assert importlib.metadata.version('markitdown')=='0.1.8';"
            f"[importlib.import_module(name) for name in {imports!r}];"
        )
        if environment == "core":
            script += "assert not any(importlib.util.find_spec(n) for n in ('speech_recognition','pydub'));"
        try:
            with environment_lock(self.root):
                run_process([str(interpreter), "-I", "-c", script])
            return True
        except (OSError, RequirementError, subprocess.TimeoutExpired):
            return False

    def ensure(self, group, environment="core"):
        if environment not in ("core", "audio"):
            raise RequirementError("Ambiente de conversão desconhecido")
        if group == "audio-transcription" and environment != "audio":
            raise RequirementError("Bibliotecas de transcrição somente podem ser adquiridas no ambiente audio")
        if not (3, 11) <= sys.version_info[:2] <= (3, 14):
            raise RequirementError("MarkItDown 0.1.8 requer Python 3.11–3.14; nenhum intérprete será baixado")
        if group not in RECIPES["groups"]:
            raise RequirementError(f"Receita desconhecida: {group}")
        if self.available(group, environment):
            return
        recipe = RECIPES["groups"][group]
        target_recipe = {**recipe, "purpose": f"{recipe['purpose']} em {self.root / environment}"}
        if not self.consent.install(f"{environment}:{group}", target_recipe):
            raise RequirementError(f"Requisito {group} ausente: {', '.join(recipe['requirements'])}. Repita em TTY para autorizar a instalação")
        uv = shutil.which("uv")
        if not uv:
            raise RequirementError("Aquisição requer uv >=0.12.13; instale uv e repita a operação")
        observed = run_process([uv, "--version"]).split()[1]
        if tuple(int(part) for part in observed.split(".")[:3]) < (0, 12, 13):
            raise RequirementError("Aquisição requer uv >=0.12.13")
        interpreter = self.python(environment)
        try:
            with environment_lock(self.root):
                if not interpreter.exists():
                    run_process([uv, "--no-config", "venv", "--python", sys.executable,
                                 "--no-python-downloads", str(self.root / environment)])
                run_process([uv, "--no-config", "pip", "install", "--python", str(interpreter),
                             "--constraints", str(RESOURCES / "constraints.txt"),
                             "--require-hashes", "--requirements", str(RESOURCES / f"{group}.txt")])
        except (OSError, RequirementError, subprocess.TimeoutExpired) as err:
            raise AcquisitionError(f"Aquisição de {group} falhou: {err}") from err
        if not self.available(group, environment):
            raise AcquisitionError(f"Instalação de {group} não passou na validação de versão/imports; repita após corrigir")

    def worker(self, request, environment="core"):
        request = {**request, "environment": environment}
        # Mesmo lock para mutações e workers: nenhum import antigo sobrevive à aquisição.
        with environment_lock(self.root):
            with subprocess.Popen([str(self.python(environment)), "-I", "-X", "utf8", str(RESOURCES / "worker.py")],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, encoding="utf-8", shell=False) as process:
                try:
                    stdout, stderr = process.communicate(json.dumps(request), timeout=300)
                except BaseException:
                    process.kill()
                    process.communicate()
                    raise
                if process.returncode:
                    raise RequirementError(f"Worker falhou ({process.returncode}): {stderr.strip()}")
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError as exc:
                    raise RequirementError("Worker retornou protocolo inválido") from exc

    def ffmpeg(self):
        candidate = shutil.which("ffmpeg")
        if candidate:
            try:
                if run_process([candidate, "-version"]).startswith("ffmpeg version"):
                    return str(Path(candidate).resolve())
            except (OSError, RequirementError, subprocess.TimeoutExpired):
                pass
        self.ensure("ffmpeg", "audio")
        with environment_lock(self.root):
            executable = run_process([str(self.python("audio")), "-I", "-c",
                                      "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"]).strip()
            if not run_process([executable, "-version"]).startswith("ffmpeg version"):
                raise RequirementError("FFmpeg portátil adquirido não passou no smoke")
        return executable

    def exiftool(self):
        candidate = shutil.which("exiftool")
        if candidate:
            try:
                if run_process([candidate, "-ver"]).strip() == "13.59":
                    return str(Path(candidate).resolve())
            except (OSError, RequirementError, subprocess.TimeoutExpired):
                pass
        system = platform.system().lower()
        if system not in RECIPES["binaries"] or platform.machine().lower() not in ("amd64", "x86_64"):
            raise RequirementError("ExifTool portátil validado somente para Windows/Linux x64")
        target = self.root / "exiftool-13.59"
        executable = target / ("exiftool.exe" if os.name == "nt" else "Image-ExifTool-13.59/exiftool")
        if executable.is_file():
            if run_process([str(executable), "-ver"]).strip() == "13.59":
                return str(executable)
            raise RequirementError("ExifTool portátil não corresponde à versão 13.59")
        if os.name != "nt" and not shutil.which("perl"):
            raise RequirementError("ExifTool 13.59 requer Perl local; instale Perl e repita. Nenhum pacote do sistema foi alterado")
        recipe = RECIPES["binaries"][system]
        if not self.consent.install("exiftool", {"requirements": ["ExifTool 13.59"], "purpose": "metadados locais de imagem/áudio", **recipe}):
            raise RequirementError("ExifTool 13.59 ausente; extração local requer aquisição consentida")
        with environment_lock(self.root):
            if executable.is_file():
                return str(executable)
            with tempfile.TemporaryDirectory(prefix="exiftool-", dir=self.root) as directory:
                scratch = Path(directory)
                archive_path = scratch / recipe["filename"]
                hasher = hashlib.sha256()
                with requests.get(recipe["url"], stream=True, timeout=(20, 60)) as response:
                    response.raise_for_status()
                    deadline = time.monotonic() + 300
                    with archive_path.open("xb") as stream:
                        for chunk in response.iter_content(65536):
                            if time.monotonic() > deadline:
                                raise RequirementError("Timeout de aquisição do ExifTool (300 segundos)")
                            hasher.update(chunk)
                            stream.write(chunk)
                if hasher.hexdigest() != recipe["sha256"]:
                    raise RequirementError("Hash SHA-256 do ExifTool diverge da receita; aquisição recusada")
                extracted = scratch / "unpacked"
                extracted.mkdir()
                if os.name == "nt":
                    with zipfile.ZipFile(archive_path) as archive:
                        for member in archive.infolist():
                            destination = (extracted / member.filename).resolve()
                            if not destination.is_relative_to(extracted.resolve()):
                                raise RequirementError("Caminho inseguro no arquivo ExifTool")
                        archive.extractall(extracted)
                    origin = next(extracted.rglob("exiftool(-k).exe"))
                    origin.rename(origin.with_name("exiftool.exe"))
                    package = origin.parent
                else:
                    with tarfile.open(archive_path) as archive:
                        archive.extractall(extracted, filter="data")
                    package = extracted
                staged = package / ("exiftool.exe" if os.name == "nt" else "Image-ExifTool-13.59/exiftool")
                if run_process([str(staged), "-ver"]).strip() != "13.59":
                    raise RequirementError("ExifTool adquirido falhou na validação de versão")
                # Extração é publicada somente após hash e smoke; nunca substitui aquisição prévia.
                package.rename(target)
        return str(executable)
