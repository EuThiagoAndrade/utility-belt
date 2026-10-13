"""Smokes reais opt-in, sem downloads incidentais ou serviços externos na suíte.

BELT_MARKDOWN_TEST_DATA aponta para ambientes adquiridos previamente pelo
smoke de desenvolvimento, após consentimento simulado da operação de teste.
"""

import os
import subprocess
from pathlib import Path

import pytest

from utility_belt.markdown import convert
from utility_belt.markdown_runtime.runtime import Runtime

FIXTURES = Path(__file__).parent / "fixtures" / "markdown"


class Refuse:
    def install(self, *_):
        pytest.fail("Smoke não pode baixar requisito ausente")

    def audio(self, *_):
        return []


@pytest.fixture
def real_runtime():
    data = os.environ.get("BELT_MARKDOWN_TEST_DATA")
    if not data:
        pytest.skip("Smoke real requer BELT_MARKDOWN_TEST_DATA com receitas previamente adquiridas")
    return Runtime(Refuse(), data_dir=data)


@pytest.mark.parametrize("name", [
    "sample.txt", "sample.md", "sample.json", "sample.jsonl", "sample.csv", "sample.html", "sample.rss",
    "sample.ipynb", "sample.epub", "sample.pdf", "sample.docx", "sample.pptx", "sample.xlsx", "sample.xls",
    "sample.msg", "sample.zip", "sample.unrecognized", "no-extension", "sample.png", "sample.jpg", "sample.wav",
    "sample.mp3", "sample.m4a", "sample.mp4",
])
def test_native_fixture(real_runtime, tmp_path, name):
    result = convert(FIXTURES / name, output_dir=tmp_path, runtime=real_runtime, consent=Refuse())
    assert result.code == 0, result.diagnostic
    assert result.output.name == name + ".md"
    text = result.output.read_text(encoding="utf-8")
    expected = "ImageSize: 16x16" if name == "sample.jpg" else "SampleRate: 16000" if name == "sample.wav" else "Utility Belt fixture"
    assert expected in text
    if name == "sample.wav":
        assert "Transcript" not in text
        assert "somente metadados" in result.diagnostic


def test_zip_corrupt_member_is_reported(real_runtime, tmp_path):
    result = convert(FIXTURES / "partial.zip", output_dir=tmp_path, runtime=real_runtime, consent=Refuse())
    assert result.code == 1 and result.status == "partial"
    assert "Utility Belt fixture" in result.output.read_text(encoding="utf-8")
    assert "broken.pdf" in result.diagnostic


@pytest.mark.parametrize("url,converter,html", [
    ("https://en.wikipedia.org/wiki/Fixture", "WikipediaConverter", '<span class="mw-page-title-main">Utility Belt fixture</span><div id="mw-content-text"><p>Utility Belt fixture</p></div>'),
    ("https://www.bing.com/search?q=fixture", "BingSerpConverter", '<li class="b_algo"><h2><a href="https://example.com">Utility Belt fixture</a></h2></li>'),
])
def test_specific_web_converters_use_fixture_snapshot(real_runtime, tmp_path, url, converter, html):
    source = tmp_path / "snapshot.html"
    source.write_text(html)
    request = {"action": "probe", "source": str(source), "stream_info": {"url": url, "mimetype": "text/html"}}
    probe = real_runtime.worker(request)
    assert probe["converters"] == [converter]
    result = real_runtime.worker({**request, "action": "convert", "expected_digest": probe["source_digest"]})
    assert result["status"] == "success"
    assert "Utility Belt fixture" in result["markdown"]


def test_audio_environment_without_consent_cannot_send(real_runtime, tmp_path):
    # Execução isolada no ambiente audio real: cliente de rede substituído por
    # função que falha, provando que instalação prévia não concede envio.
    interpreter = real_runtime.python("audio")
    if not interpreter.is_file():
        pytest.fail("Smoke requer ambiente audio previamente adquirido")
    worker = Path(__file__).parents[1] / "src" / "utility_belt" / "markdown_runtime" / "worker.py"
    source = FIXTURES / "sample.wav"
    script = f"""
import importlib.util,json
import speech_recognition
def forbidden(*args,**kwargs):
    raise AssertionError('Audio enviado sem consentimento')
speech_recognition.Recognizer.recognize_google=forbidden
spec=importlib.util.spec_from_file_location('worker',{str(worker)!r})
worker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
result=worker.execute({{'action':'convert','environment':'audio','source':{str(source)!r},'stream_info':{{'filename':'sample.wav','extension':'.wav'}},'authorized_audio':[],'exiftool':{real_runtime.exiftool()!r}}})
assert result['status']=='success',result
assert 'Transcript' not in result['markdown'],result
assert 'SampleRate: 16000' in result['markdown'],result
print(json.dumps(result))
"""
    result = subprocess.run([str(interpreter), "-I", "-X", "utf8", "-c", script],
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stderr


def test_zip_audio_without_consent_cannot_send(real_runtime, tmp_path):
    import zipfile
    archive = tmp_path / "audio.zip"
    with zipfile.ZipFile(archive, "w") as target:
        target.write(FIXTURES / "sample.wav", "sub/sample.wav")
    result = convert(archive, output_dir=tmp_path / "out", runtime=real_runtime, consent=Refuse())
    assert result.code == 0, result.diagnostic
    text = result.output.read_text(encoding="utf-8")
    assert "SampleRate: 16000" in text and "Transcript" not in text
    assert "somente metadados" in result.diagnostic


@pytest.mark.parametrize("name", ["sample.mp3", "sample.m4a", "sample.mp4"])
def test_real_ffmpeg_normalization_with_external_service_mocked(real_runtime, tmp_path, name):
    worker = Path(__file__).parents[1] / "src" / "utility_belt" / "markdown_runtime" / "worker.py"
    source = FIXTURES / name
    script = f"""
import hashlib,importlib.util,json
import speech_recognition
sent=[]
def mock_google(self,audio,**kwargs):
    assert audio.sample_rate>0 and len(audio.frame_data)>0
    sent.append(True)
    return 'Utility Belt fixture'
speech_recognition.Recognizer.recognize_google=mock_google
spec=importlib.util.spec_from_file_location('worker',{str(worker)!r})
worker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
sha=hashlib.sha256(open({str(source)!r},'rb').read()).hexdigest()
result=worker.execute({{'action':'convert','environment':'audio','source':{str(source)!r},'stream_info':{{'filename':{name!r},'extension':{Path(name).suffix!r}}},'authorized_audio':[sha],'exiftool':{real_runtime.exiftool()!r}}})
assert result['status']=='success',result
assert 'Audio Transcript' in result['markdown'],result
assert 'Utility Belt fixture' in result['markdown'],result
assert len(sent)==1,sent
print(json.dumps(result))
"""
    result = subprocess.run([str(real_runtime.python("audio")), "-I", "-X", "utf8", "-c", script],
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stderr


def test_native_youtube_caption_integration_with_service_mocked(real_runtime, tmp_path):
    worker = Path(__file__).parents[1] / "src" / "utility_belt" / "markdown_runtime" / "worker.py"
    source = FIXTURES / "sample.html"
    script = f"""
import importlib.util
from types import SimpleNamespace
from markitdown.converters import _youtube_converter
calls=[]
class Captions:
    def list(self,video):
        calls.append(video)
        return [SimpleNamespace(language_code='en')]
    def fetch(self,video,**kwargs):
        return [SimpleNamespace(text='Utility Belt fixture caption')]
_youtube_converter.YouTubeTranscriptApi=Captions
spec=importlib.util.spec_from_file_location('worker',{str(worker)!r})
worker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
request={{'action':'convert','environment':'core','source':{str(source)!r},'stream_info':{{'url':'https://www.youtube.com/watch?v=fixture','mimetype':'text/html'}}}}
result=worker.execute(request)
assert result['status']=='success',result
assert 'Transcript' in result['markdown'] and 'fixture caption' in result['markdown'],result
assert calls==['fixture'],calls
"""
    result = subprocess.run([str(real_runtime.python()), "-I", "-X", "utf8", "-c", script],
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stderr
