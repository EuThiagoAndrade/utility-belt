"""Harness opt-in: pacote instalado fora do checkout, PTY e aquisições reais.

Driver requer pexpect (Linux) ou pywinpty (Windows), somente no ambiente de teste.
O --python aponta para uma instalação mínima independente do driver.
"""

import argparse
import json
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--fixture-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--consent-install", action="store_true", required=True)
    parser.add_argument("--exercise-menu", action="store_true")
    args = parser.parse_args()
    # Resolver symlink do Python Linux escaparia da venv instalada.
    python, artifact = args.python.absolute(), args.artifact.resolve()
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", TERM="xterm-256color",
               WIN_PD_OVERRIDE_LOCAL_APPDATA=str(work / "userdata"),
               XDG_DATA_HOME=str(work / "userdata"), XDG_CONFIG_HOME=str(work / "config"))
    env.pop("PYTHONPATH", None)
    env.pop("BELT_MARKDOWN_TEST_DATA", None)
    entry = [str(python), "-X", "utf8", "-m", "utility_belt.cli"]

    def run(arguments, code=0):
        completed = subprocess.run(entry + arguments, cwd=work, env=env, capture_output=True,
                                   input="", text=True, encoding="utf-8", timeout=320)
        assert completed.returncode == code, (arguments, completed.returncode, completed.stdout, completed.stderr)
        return completed.stdout + completed.stderr

    class Terminal:
        def __init__(self, arguments):
            self.log = ""
            self.cursor = 0
            self.messages = queue.Queue()
            command = entry + arguments
            if os.name == "nt":
                from winpty import PtyProcess
                self.child = PtyProcess.spawn(subprocess.list2cmdline(command), cwd=str(work), env=env,
                                               dimensions=(30, 120))
                read = self.child.read
            else:
                import pexpect
                self.child = pexpect.spawn(command[0], command[1:], cwd=str(work), env=env,
                                          encoding="utf-8", timeout=320, dimensions=(30, 120))
                def read():
                    return self.child.read_nonblocking(4096, timeout=320)
            def collect():
                try:
                    while True:
                        chunk = read()
                        if not chunk:
                            break
                        self.messages.put(chunk)
                except (EOFError, OSError):
                    pass
                except Exception as err:
                    if type(err).__name__ not in ("EOF", "TIMEOUT"):
                        self.messages.put(f"harness read error: {err}")
                finally:
                    self.messages.put(None)
            self.thread = threading.Thread(target=collect, daemon=True)
            self.thread.start()

        def until(self, marker, timeout=320):
            deadline = time.monotonic() + timeout
            while marker not in self.log[self.cursor:]:
                chunk = self.messages.get(timeout=max(0.1, deadline - time.monotonic()))
                assert chunk is not None, self.log
                self.log += chunk
            self.cursor = self.log.index(marker, self.cursor) + len(marker)
            return self.log

        def send(self, value):
            if os.name == "nt":
                self.child.write(value)
            else:
                self.child.send(value)

        def finish(self, code):
            self.thread.join(320)
            assert not self.thread.is_alive(), self.log
            while not self.messages.empty():
                chunk = self.messages.get()
                if chunk:
                    self.log += chunk
            if os.name == "nt":
                observed = self.child.exitstatus
            else:
                self.child.close()
                observed = self.child.exitstatus
            assert observed == code, (observed, self.log)
            return self.log

    # Conteúdo do pacote, não do checkout; nenhuma dependência do motor na instalação inicial.
    inspect = subprocess.check_output([str(python), "-I", "-c",
        "import importlib.util,json;from pathlib import Path;import utility_belt;"
        "p=Path(utility_belt.__file__).parent;"
        "assert importlib.util.find_spec('markitdown') is None;"
        "assert importlib.util.find_spec('pdfplumber') is None;"
        "assert (p/'markdown_runtime/worker.py').is_file();"
        "assert (p/'markdown_runtime/pdf.txt').is_file();"
        "assert (p/'tools/markdown_convert/tool.toml').is_file();"
        "print(json.dumps({'package':str(p),'python':__import__('sys').version}))"], cwd=work, env=env, text=True)
    assert "site-packages" in inspect.lower(), inspect
    print(inspect, flush=True)
    assert "markdown.convert" in run(["list", "--json"])
    shutil.copyfile(args.fixture_dir / "sample.pdf", work / "sample.pdf")
    shutil.copyfile(args.fixture_dir / "sample.txt", work / "sample.txt")
    command = ["markdown", "convert", "sample.pdf", "--output-dir", "output"]
    run(command, 2)  # Não-TTY, nenhuma aquisição.
    run(["run", "markdown.convert", "--non-interactive", "convert", "sample.pdf", "--output-dir", "output"], 2)
    terminal = Terminal(command + ["--non-interactive"])
    assert "[s/N]" not in terminal.finish(2)
    terminal = Terminal(command)
    terminal.until("[s/N]")
    terminal.send("n\r")
    terminal.finish(2)
    assert not list(work.rglob(".lock")), "Recusa/não-TTY mutaram runtime"
    terminal = Terminal(command)
    terminal.until("[s/N]")
    terminal.send("s\r")
    # Cada receita necessária tem consentimento próprio; base e PDF somente.
    terminal.until("markitdown[pdf]==0.1.8")
    terminal.send("s\r")
    acquired = terminal.finish(0)
    assert "Salvo em:" in acquired
    assert "docx" not in acquired and "audio-transcription" not in acquired
    print("TTY: recusa=2; modo não interativo=2; aquisição base+PDF=0", flush=True)
    print(run(["markdown", "config", "--output-dir", "central"]), flush=True)
    config_before = list(work.rglob("config.toml"))[0].read_bytes()
    run(["markdown", "convert", "sample.pdf", "--non-interactive"])
    run(["run", "markdown.convert", "--non-interactive", "convert", "sample.pdf"])
    assert len({path.read_bytes() for path in (work / "central").rglob("sample.pdf.md")}) == 1
    assert list(work.rglob("config.toml"))[0].read_bytes() == config_before
    source = work / "source/deep"
    source.mkdir(parents=True)
    shutil.copyfile(work / "sample.txt", source / "file.txt")
    run(["markdown", "batch", "source", "--non-interactive"])
    # Ambiente adquirido sobrevive à reinstalação compatível do Belt.
    doctor = json.loads(run(["doctor", "markdown", "--json"]))["markdown"]
    runtime = Path(doctor["path"])
    interpreter = Path(doctor["environments"]["core"]["python"])
    previous = interpreter.stat().st_mtime_ns
    assert doctor["environments"]["core"]["groups"]["pdf"]
    subprocess.run(["uv", "--no-config", "pip", "install", "--python", str(python),
                    "--reinstall-package", "utility-belt", str(artifact)], check=True, cwd=work, env=env)
    run(["markdown", "convert", "sample.pdf", "--non-interactive"])
    assert interpreter.stat().st_mtime_ns == previous
    assert not (runtime / "audio").exists()
    terminal = Terminal(["markdown", "watch", "source", "--non-interactive"])
    terminal.until("Monitor ativo")
    (source / "new.txt").write_text("Utility Belt distributed monitor fixture", encoding="utf-8")
    terminal.until("Salvo em:")
    terminal.send("\x03")
    terminal.finish(130)
    assert any("distributed monitor" in p.read_text(encoding="utf-8") for p in (work / "central").rglob("*.md"))
    # Sessão descartável X11: clipboard real, sem tocar no clipboard do responsável.
    clipboard_status = "backend Windows preservado; conversão controlada na suíte"
    if os.name != "nt":
        if env.get("DISPLAY"):
            subprocess.run(["xclip", "-selection", "clipboard"], input=str(work / "sample.txt"),
                           text=True, env=env, check=True)
            run(["markdown", "clipboard", "--non-interactive"])
            clipboard_status = "clipboard X11 real convertido=0"
        else:
            run(["markdown", "clipboard", "--non-interactive"], 2)
            clipboard_status = "headless clipboard indisponível=2"
    # TTY de menu real: cancelar seleção inicial retorna ao shell.
    terminal = Terminal(["markdown", "menu"])
    terminal.until("Markdown")
    terminal.send("\x03")
    terminal.finish(0)
    if args.exercise_menu:
        for value, marker in [("sample.pdf", "Salvo em:"), ("missing.pdf", "Entrada"), ("", "Operação cancelada.")]:
            terminal = Terminal(["markdown"])
            terminal.until("Escolha uma opção")
            terminal.send("\r")
            terminal.until("vazio cancela")
            terminal.send(value + "\r")
            terminal.until(marker)
            terminal.until("Pressione qualquer tecla")
            terminal.send("\r")
            terminal.until("Escolha uma opção")
            terminal.send("\x1b[B" * 5 + "\r")
            terminal.finish(0)
        print("Menu TTY real: sucesso, erro e cancelamento retornaram ao submenu", flush=True)
    outputs = sorted(str(p.relative_to(work)) for folder in (work / "output", work / "central")
                     for p in folder.rglob("*.md"))
    evidence = {"package": json.loads(inspect), "runtime": str(runtime), "outputs": outputs,
                "clipboard": clipboard_status, "reuse_upgrade": True, "watch_exit": 130}
    (work / "evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
