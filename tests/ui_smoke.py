"""Renderiza Questionary em terminal VT simulado e exercita navegação real.

uv run --with pyte --with pillow python tests/ui_smoke.py --output preview.png
Dependências opcionais somente para QA; nenhuma ferramenta externa é executada.
"""

import argparse
import io
import os
import threading
from pathlib import Path
from unittest.mock import patch

import pyte
from PIL import Image, ImageDraw, ImageFont
from prompt_toolkit.application import create_app_session
from prompt_toolkit.data_structures import Size
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.output.vt100 import Vt100_Output

from utility_belt import menu


class Terminal(io.StringIO):
    @property
    def encoding(self):
        return "utf-8"

    def isatty(self):
        return True

    def write(self, text):
        return super().write(text.replace("\r\n", "\n").replace("\n", "\r\n"))


def capture():
    stream = Terminal()
    snapshot = []
    failures = []
    with create_pipe_input() as keyboard, patch.dict(os.environ):
        os.environ.pop("NO_COLOR", None)
        os.environ["TERM"] = "xterm-256color"
        output = Vt100_Output(stream, lambda: Size(rows=36, columns=96), term="xterm-256color",
                             default_color_depth=ColorDepth.DEPTH_24_BIT, enable_cpr=False)
        def keys():
            try:
                # Esperar cada tela renderizar; esta espera pertence ao harness.
                import time
                time.sleep(0.4)
                keyboard.send_text("\x1b[B\x1b[B")
                time.sleep(0.4)
                snapshot.append(stream.getvalue())
                # Sistema -> Sobre -> confirmar retorno -> voltar -> sair.
                keyboard.send_text("\x1b[B\r")
                time.sleep(0.3)
                keyboard.send_text("\x1b[B\x1b[B\r")
                time.sleep(0.3)
                keyboard.send_text("x")
                time.sleep(0.3)
                keyboard.send_text("\x03")
                time.sleep(0.3)
                keyboard.send_text("\x03")
            except Exception as exc:
                failures.append(exc)
                keyboard.send_text("\x03")
        worker = threading.Thread(target=keys, daemon=True)
        with create_app_session(input=keyboard, output=output), patch("sys.stdout", stream), \
             patch("sys.stdin.isatty", return_value=True), patch.object(menu, "clear_screen", lambda: None), \
             patch("utility_belt.ui.screen.clear_screen", lambda: None), \
             patch("utility_belt.ui.screen.get_terminal_width", return_value=96):
            worker.start()
            menu.show_menu()
            worker.join(timeout=5)
    assert not failures and not worker.is_alive(), failures
    transcript = stream.getvalue()
    assert "Sobre o Utility Belt" in transcript and "Pressione qualquer tecla" in transcript
    assert "Até logo" in transcript or "Encerrando menu" in transcript
    screen = pyte.Screen(96, 36)
    pyte.Stream(screen).feed(snapshot[0])
    visible = "\n".join(row.rstrip() for row in screen.display).rstrip() + "\n"
    assert all(word in visible for word in ("UTILITY BELT", "Restic", "Docker", "Markdown", "Sistema")), visible
    assert "> [3] Markdown" in visible, visible
    return screen, visible


def render(screen, output_path):
    font_candidates = [Path("C:/Windows/Fonts/consola.ttf"),
                       Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")]
    font_path = next((path for path in font_candidates if path.exists()), None)
    font = ImageFont.truetype(str(font_path), 20) if font_path else ImageFont.load_default()
    cell_w = int(font.getlength("M") + 1)
    cell_h, padding = 29, 30
    occupied = max(i for i, row in enumerate(screen.display) if row.strip()) + 2
    image = Image.new("RGB", (screen.columns * cell_w + padding * 2, occupied * cell_h + padding * 2), "#10151a")
    draw = ImageDraw.Draw(image)
    names = {"default": "#e6edf3", "black": "#10151a", "white": "#e6edf3", "cyan": "#51d4e8",
             "brown": "#f0b84b", "green": "#80ce98", "red": "#f47b7b", "brightblack": "#9299a5"}
    def color(value):
        return names.get(value, "#" + value if len(value) == 6 else "#9299a5")
    for row in range(occupied):
        for col in range(screen.columns):
            char = screen.buffer[row][col]
            x, y = padding + col * cell_w, padding + row * cell_h
            if char.bg != "default":
                draw.rectangle((x, y, x + cell_w, y + cell_h), fill=color(char.bg))
            draw.text((x, y), char.data, font=font, fill=color(char.fg))
    image.save(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    terminal, visible = capture()
    render(terminal, args.output)
    args.output.with_suffix(".txt").write_text(visible, encoding="utf-8")
    print(f"Smoke de navegação VT passou. Preview: {args.output.resolve()}")
