"""Worker standalone: protocolo JSON, executado com Python -I na venv própria.

As adaptações abaixo protegem consentimento e tornam falhas de ZIP visíveis.
Detecção e conversão permanecem nos conversores nativos da release fixada.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import zipfile
from importlib.metadata import version
from pathlib import Path

GROUPS = {
    "PdfConverter": "pdf",
    "DocxConverter": "docx",
    "PptxConverter": "pptx",
    "XlsxConverter": "xlsx",
    "XlsConverter": "xls",
    "OutlookMsgConverter": "outlook",
    "YouTubeConverter": "youtube-transcription",
}


def digest(stream):
    position = stream.tell()
    try:
        return hashlib.sha256(stream.read()).hexdigest()
    finally:
        stream.seek(position)


def execute(request):
    from markitdown import FileConversionException, MarkItDown, StreamInfo, UnsupportedFormatException
    from markitdown.converters import _audio_converter, _transcribe_audio

    if version("markitdown") != "0.1.8":
        raise RuntimeError("Versão do motor incompatível; esperado MarkItDown 0.1.8")
    if request["environment"] == "core" and any(
        importlib.util.find_spec(name) for name in ("speech_recognition", "pydub")
    ):
        raise RuntimeError("Ambiente core contém bibliotecas de transcrição; conversão recusada")

    engine = MarkItDown(enable_plugins=False, exiftool_path=request.get("exiftool") or "")
    raw = Path(request["source"]).read_bytes()
    source_digest = hashlib.sha256(raw).hexdigest()
    if request.get("expected_digest") and request["expected_digest"] != source_digest:
        raise RuntimeError("Entrada mudou após preflight; repita a operação")
    info = StreamInfo(**request["stream_info"])
    groups, audio, converters = set(), [], set()
    # Detecção usa o registro e as mesmas hipóteses do motor, inclusive conteúdo.
    def inspect(stream, base, label, depth=0):
        if depth > 20:
            raise ValueError("Profundidade de arquivos ZIP excede 20 níveis")
        for guess in engine._get_stream_info_guesses(stream, base):
            for registration in sorted(engine._converters, key=lambda item: item.priority):
                converter = registration.converter
                if converter.accepts(stream, guess):
                    name = type(converter).__name__
                    converters.add(name)
                    if name in GROUPS:
                        groups.add(GROUPS[name])
                    if name in ("AudioConverter", "ImageConverter"):
                        groups.add("exiftool")
                    if name == "AudioConverter":
                        audio.append({"name": label, "sha256": digest(stream), "extension": guess.extension})
                    if name == "ZipConverter":
                        with zipfile.ZipFile(stream) as archive:
                            for member in archive.infolist():
                                if member.is_dir():
                                    continue
                                data = io.BytesIO(archive.read(member))
                                member_info = StreamInfo(
                                    filename=Path(member.filename).name,
                                    extension=Path(member.filename).suffix,
                                )
                                inspect(data, member_info, f"{label}!{member.filename}", depth + 1)
                    return

    inspect(io.BytesIO(raw), info, request.get("label", info.filename or "URL"))
    if request["action"] == "probe":
        return {"status": "ready", "groups": sorted(groups), "audio": audio,
                "converters": sorted(converters), "source_digest": source_digest}

    permitted = set(request.get("authorized_audio", []))
    actual = {item["sha256"] for item in audio}
    if permitted - actual:
        raise RuntimeError("Conjunto de áudio mudou após consentimento")
    native_transcribe = _transcribe_audio.transcribe_audio

    def transcribe(stream, *, audio_format="wav"):
        if digest(stream) not in permitted:
            # Mesmo em ambiente audio previamente instalado, ausência de autorização
            # impede toda chamada ao serviço. Metadados locais continuam possíveis.
            from markitdown import MissingDependencyException
            raise MissingDependencyException("Transcrição externa não autorizada nesta operação")
        if audio_format == "wav":
            return native_transcribe(stream, audio_format="wav")
        binary = request.get("ffmpeg")
        if not binary:
            import imageio_ffmpeg
            binary = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.TemporaryDirectory(prefix="belt-audio-") as directory:
            source = Path(directory) / ("source." + audio_format)
            target = Path(directory) / "normalized.wav"
            position = stream.tell()
            try:
                source.write_bytes(stream.read())
            finally:
                stream.seek(position)
            subprocess.run([binary, "-nostdin", "-y", "-i", str(source), str(target)],
                           check=True, capture_output=True, timeout=120)
            with target.open("rb") as normalized:
                return native_transcribe(normalized, audio_format="wav")

    _audio_converter.transcribe_audio = transcribe
    failures = []
    payloads = []
    native_stream = engine.convert_stream
    member_stack = []
    # O motor pode tentar um fallback genérico depois de um conversor específico
    # falhar. Registrar tentativas também evita ocultar PDF corrompido em ZIP.
    for registration in engine._converters:
        converter = registration.converter
        original = converter.convert

        def observed(stream, stream_info, *, _original=original, _name=type(converter).__name__, **kwargs):
            try:
                return _original(stream, stream_info, **kwargs)
            except Exception as exc:
                if member_stack and _name != "ZipConverter":
                    entry = {"member": member_stack[-1], "error": f"{_name}: {type(exc).__name__}: {exc}"}
                    if entry not in failures:
                        failures.append(entry)
                raise

        converter.convert = observed

    def tracked_stream(stream, *, stream_info=None, **kwargs):
        if not stream.getbuffer().nbytes and not getattr(stream_info, "filename", None):
            raise UnsupportedFormatException("Diretório ZIP não é documento")
        member_stack.append(getattr(stream_info, "filename", None))
        try:
            result = native_stream(stream, stream_info=stream_info, **kwargs)
            if not result.markdown.strip():
                raise FileConversionException("Conversor não produziu conteúdo")
            # Diretórios não são documentos; o ZIP nativo pode tentar convertê-los.
            if stream.getbuffer().nbytes:
                payloads.append(result.markdown)
            return result
        except (UnsupportedFormatException, FileConversionException) as exc:
            failures.append({"member": getattr(stream_info, "filename", None), "error": str(exc)})
            raise
        finally:
            member_stack.pop()

    engine.convert_stream = tracked_stream
    try:
        result = native_stream(io.BytesIO(raw), stream_info=info)
        text = result.markdown
        if not text.strip() or ("ZipConverter" in converters and not payloads):
            return {"status": "failed", "diagnostic": "Conversor não produziu conteúdo útil", "markdown": ""}
        return {"status": "partial" if failures else "success", "markdown": text, "failures": failures,
                "diagnostic": "Áudio sem consentimento: somente metadados locais" if actual - permitted else ""}
    except UnsupportedFormatException as exc:
        return {"status": "unsupported", "markdown": "", "diagnostic": str(exc)}
    except FileConversionException as exc:
        missing = []
        for attempt in exc.attempts or []:
            if attempt.exc_info and attempt.exc_info[0].__name__ == "MissingDependencyException":
                group = GROUPS.get(type(attempt.converter).__name__)
                if group:
                    missing.append(group)
        return {"status": "missing" if missing else "failed", "groups": sorted(set(missing)),
                "markdown": "", "diagnostic": str(exc)}
    finally:
        _audio_converter.transcribe_audio = native_transcribe


def main():
    try:
        request = json.load(sys.stdin)
        # Bibliotecas não podem contaminar stdout do protocolo com avisos.
        with contextlib.redirect_stdout(sys.stderr):
            result = execute(request)
    except Exception as exc:
        result = {"status": "failed", "markdown": "", "diagnostic": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
