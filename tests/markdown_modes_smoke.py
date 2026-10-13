"""Smokes reais do Item 2 em ambiente explícito; nunca autoriza áudio externo."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from utility_belt.markdown_runtime.runtime import Runtime


class DevelopmentConsent:
    def install(self, group, recipe):
        print(f"Smoke: aquisição consentida de {group}", flush=True)
        return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--consent-install", action="store_true", required=True)
    arguments = parser.parse_args()
    runtime = Runtime(DevelopmentConsent(), data_dir=arguments.data_dir.resolve())
    for group in ["base", "pdf", "docx"]:
        runtime.ensure(group)
    for group in ["base", "audio-transcription"]:
        runtime.ensure(group, "audio")
    print(f"Smoke: ExifTool {runtime.exiftool()}", flush=True)
    os.environ["BELT_MARKDOWN_TEST_DATA"] = str(arguments.data_dir.resolve())
    subprocess.run([sys.executable, "-m", "pytest", "tests/test_markdown_batch.py",
                    "tests/test_markdown_watch.py", "tests/test_markdown_modes_integration.py",
                    "-q", "-p", "no:cacheprovider"], check=True)


if __name__ == "__main__":
    main()
