"""Gera a demonstração dos menus reais, sem executar suas operações.

Na raiz do checkout:
    uv run --with pyte --with pillow python scripts/generate_demo.py
    uv run --with pyte --with pillow python scripts/generate_demo.py --self-check

Captura saída VT de Questionary com teclado controlado e renderiza em GIF;
não grava a janela nativa. Apenas o harness adapta limpeza ANSI, tamanho,
configuração temporária e disponibilidade de Restic/Docker. Não consulta serviços.
As operações, subprocessos e gravações de configuração são bloqueados.
Dependências opcionais de geração: pyte e Pillow; nenhuma mudança no produto.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import io
import json
import math
import os
import tempfile
from contextlib import ExitStack
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import pyte
import questionary
from PIL import Image, ImageDraw, ImageFont
from prompt_toolkit.application import create_app_session
from prompt_toolkit.data_structures import Size
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.output.vt100 import Vt100_Output
from questionary.prompts.common import InquirerControl

from utility_belt import config, menu
from utility_belt.ui import dev_menu, docker_menu, guard, markdown_menu, restic_menu, screen

COLUMNS, ROWS = 96, 38
MAX_BYTES = 5_000_000
MODULES = (menu, restic_menu, docker_menu, markdown_menu, dev_menu)
ROUTE = (
    ("main", "restic"), ("restic", "exit"),
    ("main", "docker"), ("docker", "exit"),
    ("main", "markdown"), ("markdown", "exit"),
    ("main", "dev"), ("dev", "exit"),
    ("main", "system"), ("system", "exit"), ("main", "sair"),
)


class CaptureAborted(BaseException):
    """Escapa também dos menus que capturam Exception para mostrar um erro."""


class Terminal(io.StringIO):
    def __init__(self):
        super().__init__()
        self.screen = pyte.Screen(COLUMNS, ROWS)
        self.vt = pyte.Stream(self.screen)

    @property
    def encoding(self):
        return "utf-8"

    def isatty(self):
        return True

    def write(self, text):
        self.vt.feed(text.replace("\r\n", "\n").replace("\n", "\r\n"))
        return len(text)


class Capture:
    def __init__(self, timeout=5.0, fault=None):
        self.timeout, self.fault = timeout, fault
        self.terminal = Terminal()
        self.frames = []
        self.visited = []
        self.failures = []
        self.controllers = []
        self.dependencies = []

    def block(self, *args, **kwargs):
        self.failures.append("Tentativa de operação, subprocesso ou persistência")
        raise CaptureAborted(self.failures[-1])

    def dependency(self, name):
        self.dependencies.append(name)
        if self.dependencies != ["restic", "docker"][:len(self.dependencies)]:
            self.block()
        return True

    def frame(self, duration):
        self.frames.append((copy.deepcopy(self.terminal.screen), duration))

    def prompt_for(self, owner):
        def prompt(factory, text, **kwargs):
            if self.failures or len(self.visited) >= len(ROUTE) or factory is not questionary.select:
                self.block()
            values = [c.value for c in kwargs["choices"] if not c.disabled]
            kind = ("main" if "restic" in values else "system") if owner == "main" else owner
            expected, target = ROUTE[len(self.visited)]
            if kind != expected or target not in values:
                self.block()
            step = len(self.visited)
            self.visited.append(kind)
            # Mesmo prompt e mesmas escolhas do programa; nenhuma resposta é simulada.
            import typer

            typer.echo()
            question = factory(text, **kwargs)
            app = question.application
            control = next(c for c in app.layout.find_all_controls() if isinstance(c, InquirerControl))
            rendered = asyncio.Event()
            app.after_render += lambda _: rendered.set()
            completed = False

            async def drive():
                nonlocal completed
                try:
                    if self.fault == "timeout":
                        # Verificação negativa: esperar um estado que nunca será renderizado.
                        await asyncio.wait_for(asyncio.Event().wait(), self.timeout)
                    await asyncio.wait_for(rendered.wait(), self.timeout)
                    self.frame(3000 if step == 0 or kind != "main" else 800)
                    if self.fault == "operation":
                        # Mesmo com a exceção absorvida, o registro independente
                        # deve recusar a captura antes de entrar no próximo menu.
                        try:
                            menu.run_dedicated_screen("fault", lambda: None)
                        except CaptureAborted:
                            pass
                    for _ in range(len(values)):
                        if control.get_pointed_at().value == target:
                            break
                        rendered.clear()
                        self.keyboard.send_text("\x1b[B")
                        await asyncio.wait_for(rendered.wait(), self.timeout)
                        self.frame(140)
                    if control.get_pointed_at().value != target:
                        self.block()
                    self.frame(600)
                    completed = True
                    self.keyboard.send_text("\r")
                except (Exception, CaptureAborted) as exc:
                    self.failures.append(f"{type(exc).__name__}: {exc}")
                    if not app.is_done:
                        app.exit(result=None)

            def start():
                self.controllers.append(app.create_background_task(drive()))

            app.pre_run_callables.append(start)
            answer = question.ask()
            if self.failures or not completed or answer != target:
                self.block()
            return answer

        return prompt

    def run(self):
        try:
            with tempfile.TemporaryDirectory(prefix="belt-demo-") as temporary, ExitStack() as stack:
                root = Path(temporary)
                stack.enter_context(patch.dict(os.environ, {"TERM": "xterm-256color"}))
                os.environ.pop("NO_COLOR", None)
                for name in ("get_config_dir", "get_data_dir", "get_log_dir", "get_state_dir"):
                    path = root / name
                    path.mkdir()
                    stack.enter_context(patch.object(config, name, return_value=path))
                for name in ("save_config", "save_markdown_output_dir", "set_profile"):
                    stack.enter_context(patch.object(config, name, self.block))
                stack.enter_context(patch("subprocess.run", self.block))
                stack.enter_context(patch("subprocess.Popen", self.block))
                stack.enter_context(patch("os.system", self.block))
                stack.enter_context(patch.object(guard, "ensure_dependency", self.dependency))
                stack.enter_context(patch.object(screen, "get_terminal_width", return_value=COLUMNS))
                for module in (*MODULES, screen):
                    stack.enter_context(patch.object(module, "clear_screen", lambda: self.terminal.write("\x1b[2J\x1b[H")))
                    stack.enter_context(patch.object(module, "run_dedicated_screen", self.block))
                for module, owner in zip(MODULES, ("main", "restic", "docker", "markdown", "dev"), strict=True):
                    stack.enter_context(patch.object(module, "prompt", self.prompt_for(owner)))
                self.keyboard = stack.enter_context(create_pipe_input())
                output = Vt100_Output(
                    self.terminal, lambda: Size(rows=ROWS, columns=COLUMNS), term="xterm-256color",
                    default_color_depth=ColorDepth.DEPTH_24_BIT, enable_cpr=False,
                )
                stack.enter_context(create_app_session(input=self.keyboard, output=output))
                stack.enter_context(patch("sys.stdout", self.terminal))
                stack.enter_context(patch("sys.stdin.isatty", return_value=True))
                menu.show_menu()
        except CaptureAborted as exc:
            raise RuntimeError(f"Captura recusada: {self.failures}") from exc
        finally:
            if any(not task.done() for task in self.controllers):
                raise RuntimeError("Controlador de teclado não terminou")
        if self.failures or self.visited != [kind for kind, _ in ROUTE] or self.dependencies != ["restic", "docker"]:
            raise RuntimeError(f"Roteiro incompleto ou tentativa de operação: {self.failures}")
        return self.frames


def render(frames):
    font_path = next((p for p in (
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ) if p.is_file()), None)
    if font_path is None:
        raise RuntimeError("Instale Consolas ou DejaVu Sans Mono para gerar a demonstração")
    font = ImageFont.truetype(str(font_path), 20)
    bold_path = font_path.with_name("consolab.ttf" if os.name == "nt" else "DejaVuSansMono-Bold.ttf")
    bold = ImageFont.truetype(str(bold_path), 20) if bold_path.exists() else font
    cell_w, cell_h, padding = math.ceil(font.getlength("M")), 26, 24
    occupied = max(i for terminal, _ in frames for i, line in enumerate(terminal.display) if line.strip()) + 2
    colors = {
        "black": "#10151a", "white": "#e6edf3", "cyan": "#51d4e8", "brown": "#f0b84b",
        "green": "#80ce98", "red": "#f47b7b", "blue": "#559ee8", "magenta": "#bc8cff",
        "brightblack": "#9299a5", "brightwhite": "#ffffff", "brightcyan": "#8ae9f4",
        "brightgreen": "#a6edb0", "brightred": "#ffa0a0", "brightblue": "#8ab8ff",
        "brightmagenta": "#d9b2ff", "brightyellow": "#ffe29a", "yellow": "#f0b84b",
    }

    def color(value, default):
        if value == "default":
            return default
        return colors.get(value, f"#{value}" if len(value) == 6 else "#9299a5")

    images = []
    for terminal, _ in frames:
        image = Image.new("RGB", (COLUMNS * cell_w + padding * 2, occupied * cell_h + padding * 2), "#10151a")
        draw = ImageDraw.Draw(image)
        for row in range(min(occupied, ROWS)):
            for col in range(COLUMNS):
                char = terminal.buffer[row][col]
                x, y = padding + col * cell_w, padding + row * cell_h
                fg, bg = color(char.fg, "#e6edf3"), color(char.bg, "#10151a")
                if char.reverse:
                    fg, bg = bg, fg
                draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), fill=bg)
                draw.text((x, y), char.data, font=bold if char.bold else font, fill=fg)
        images.append(image)
    palette = images[0].quantize(colors=128)
    return [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]


def validate(path):
    with Image.open(path) as gif:
        duration, count = 0, 0
        if gif.format != "GIF" or gif.info.get("loop") != 0:
            raise ValueError("A demonstração precisa ser GIF em loop")
        dimensions = gif.size
        for index in range(gif.n_frames):
            gif.seek(index)
            gif.load()
            duration += gif.info.get("duration", 0)
            count += 1
            if gif.size != dimensions:
                raise ValueError("Resolução variável")
    size = path.stat().st_size
    if not 25_000 <= duration <= 35_000 or not 960 <= dimensions[0] <= 1280 or size > MAX_BYTES:
        raise ValueError(f"GIF fora dos limites: {duration} ms, {dimensions}, {size} bytes")
    return {"duration_ms": duration, "dimensions": dimensions, "bytes": size, "frames": count}


def publish(images, durations, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".gif", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        images[0].save(
            temporary, format="GIF", save_all=True, append_images=images[1:],
            duration=durations, loop=0, optimize=True, disposal=1,
        )
        result = validate(temporary)
        temporary.replace(destination)
        return result
    finally:
        temporary.unlink(missing_ok=True)


def self_check():
    """Exercita falhas sem operações reais; não produz a mídia de entrega."""
    original = menu.run_dedicated_screen
    for fault in ("operation", "timeout"):
        capture = Capture(timeout=0.15, fault=fault)
        try:
            capture.run()
        except RuntimeError:
            if not capture.failures or any(not task.done() for task in capture.controllers):
                raise AssertionError(f"Falha não observada/encerrada: {fault}") from None
        else:
            raise AssertionError(f"Captura inválida aceita: {fault}")
        if menu.run_dedicated_screen is not original:
            raise AssertionError("Adaptações não foram restauradas")
    with tempfile.TemporaryDirectory(prefix="belt-demo-check-") as temporary:
        destination = Path(temporary) / "existing.gif"
        destination.write_bytes(b"previous-valid-artifact")
        try:
            publish([Image.new("RGB", (16, 16))], [100], destination)
        except ValueError:
            if destination.read_bytes() != b"previous-valid-artifact" or len(list(Path(temporary).iterdir())) != 1:
                raise AssertionError("Falha substituiu destino ou deixou arquivo parcial") from None
        else:
            raise AssertionError("GIF fora dos limites aceito")
    print("Self-check OK: operação bloqueada, timeout, restauração e preservação do destino.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "docs/assets/demo.gif")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    capture = Capture()
    frames = capture.run()
    result = publish(render(frames), [duration for _, duration in frames], args.output)
    result.update({
        "output": str(args.output.resolve()), "screens": capture.visited, "blocked_attempts": len(capture.failures),
        "versions": {name: version(name) for name in ("pyte", "Pillow", "questionary", "prompt_toolkit")},
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
