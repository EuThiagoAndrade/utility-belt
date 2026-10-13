"""Aquisição real opt-in para a matriz de desenvolvimento do ciclo 006.

Nunca concede envio de áudio; ambiente e saídas ficam no diretório explícito.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from utility_belt.markdown_runtime.runtime import Runtime


class DevelopmentConsent:
    def install(self, group, recipe):
        print(f"Smoke: aquisição consentida de {group}: {recipe['requirements']}", flush=True)
        return True

    def audio(self, *_):
        return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--consent-install", action="store_true", required=True)
    args = parser.parse_args()
    directory = args.data_dir.resolve()
    runtime = Runtime(DevelopmentConsent(), data_dir=directory)
    for environment, groups in [
        ("core", ["base", "pdf", "docx", "pptx", "xlsx", "xls", "outlook", "youtube-transcription"]),
        ("audio", ["base", "audio-transcription", "ffmpeg"]),
    ]:
        for group in groups:
            runtime.ensure(group, environment)
    print(f"Smoke: ExifTool {runtime.exiftool()}", flush=True)
    os.environ["BELT_MARKDOWN_TEST_DATA"] = str(directory)
    subprocess.run([sys.executable, "-m", "pytest", "tests/test_markdown_integration.py", "-q", "-p", "no:cacheprovider"], check=True)


if __name__ == "__main__":
    main()
