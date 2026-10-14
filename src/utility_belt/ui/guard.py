"""Validação prévia de dependências externas (preflight guard) e onboarding assistido."""

from __future__ import annotations

import shutil
import sys
import webbrowser
from typing import Any

import questionary
import typer

from utility_belt.ui.screen import (
    clear_screen,
    menu_footer,
    menu_options,
    menu_separator,
    menu_style,
    message,
    prompt,
    render_header,
)

DEPENDENCY_INFO: dict[str, dict[str, Any]] = {
    "restic": {
        "name": "Restic",
        "binary": "restic",
        "description": (
            "O Restic é um utilitário de backup rápido, seguro e criptografado.\n"
            "Para utilizar este módulo, é necessário tê-lo instalado no computador."
        ),
        "windows_instructions": (
            "Comandos recomendados (PowerShell ou Windows Terminal):\n\n"
            "  winget install restic.restic\n"
            "  ou\n"
            "  scoop install restic\n\n"
            "Alternativa portátil:\n"
            "  1. Baixe o executável compactado em:\n"
            "     https://github.com/restic/restic/releases\n"
            "  2. Extraia o restic.exe e mova-o para uma pasta incluída no PATH do sistema."
        ),
        "linux_instructions": (
            "Comandos recomendados no terminal:\n\n"
            "  Debian / Ubuntu : sudo apt update && sudo apt install restic\n"
            "  Fedora / RHEL   : sudo dnf install restic\n"
            "  Arch Linux      : sudo pacman -S restic\n\n"
            "Alternativa binária direta:\n"
            "  Baixe o executável oficial em https://github.com/restic/restic/releases\n"
            "  e coloque-o em /usr/local/bin/restic (com permissão de execução chmod +x)."
        ),
        "download_url": "https://restic.net",
        "releases_url": "https://github.com/restic/restic/releases",
    },
    "docker": {
        "name": "Docker",
        "binary": "docker",
        "description": (
            "O Docker é necessário para exportar e importar imagens de contêineres.\n"
            "Para utilizar este módulo, é necessário tê-lo instalado no computador."
        ),
        "windows_instructions": (
            "Instalação recomendada no Windows:\n\n"
            "  winget install Docker.DockerDesktop\n\n"
            "Ou baixe o instalador oficial do Docker Desktop:\n"
            "  https://www.docker.com/products/docker-desktop\n\n"
            "Requisitos no Windows:\n"
            "  - WSL 2 (Subsistema do Windows para Linux) ou Hyper-V ativado.\n"
            "  - Executar o Docker Desktop e aguardar o motor iniciar."
        ),
        "linux_instructions": (
            "Instalação recomendada no Linux:\n\n"
            "  Siga o guia de instalação oficial do Docker Engine:\n"
            "  https://docs.docker.com/engine/install/\n\n"
            "Após instalar, inicie o serviço do daemon:\n"
            "  sudo systemctl enable --now docker\n\n"
            "Para rodar sem sudo, adicione seu usuário ao grupo docker:\n"
            "  sudo usermod -aG docker $USER"
        ),
        "download_url": "https://www.docker.com/products/docker-desktop",
        "releases_url": "https://docs.docker.com/engine/install/",
    },
}


def check_dependency_installed(dep_key: str) -> bool:
    """Verifica se o binário principal da dependência está presente no PATH."""
    info = DEPENDENCY_INFO.get(dep_key)
    if not info:
        return True
    return shutil.which(info["binary"]) is not None


def show_installation_instructions(dep_key: str) -> None:
    """Exibe instruções detalhadas de instalação para o sistema operacional atual."""
    info = DEPENDENCY_INFO[dep_key]
    clear_screen()
    render_header(["UTILITY BELT", info["name"].upper(), "INSTRUÇÕES DE INSTALAÇÃO"])
    typer.echo()

    instructions = (
        info["windows_instructions"]
        if sys.platform == "win32"
        else info["linux_instructions"]
    )
    message("INFO", f"Guia de instalação do {info['name']}:", details=instructions)
    typer.echo()

    if sys.stdin.isatty():
        try:
            questionary.press_any_key_to_continue(
                "Pressione qualquer tecla para voltar...", style=menu_style()
            ).ask()
        except (KeyboardInterrupt, EOFError):
            pass


def open_download_page(dep_key: str) -> None:
    """Abre a página oficial de download no navegador e sempre exibe a URL no terminal."""
    info = DEPENDENCY_INFO[dep_key]
    url = info.get("download_url") or info.get("releases_url", "")

    clear_screen()
    render_header(["UTILITY BELT", info["name"].upper(), "DOWNLOAD"])
    typer.echo()

    opened = False
    try:
        opened = webbrowser.open(url)
    except Exception:
        opened = False

    if opened:
        message("SUCESSO", "Navegador acionado com a página oficial de download.", details=f"Endereço: {url}")
    else:
        message("INFO", "Página oficial de download:", details=f"Acesse pelo seu navegador: {url}")

    typer.echo()
    if sys.stdin.isatty():
        try:
            questionary.press_any_key_to_continue(
                "Pressione qualquer tecla para voltar...", style=menu_style()
            ).ask()
        except (KeyboardInterrupt, EOFError):
            pass


def show_dependency_guard(dep_key: str) -> bool:
    """Exibe a tela dedicada de onboarding/guard para dependência ausente."""
    info = DEPENDENCY_INFO.get(dep_key)
    if not info:
        return True

    while True:
        clear_screen()
        render_header(["UTILITY BELT", info["name"].upper(), "REQUISITO AUSENTE"])
        typer.echo()
        message(
            "AVISO",
            f"O executável '{info['binary']}' não foi encontrado no sistema.",
            details=info["description"],
        )
        typer.echo()

        try:
            choice = prompt(
                questionary.select,
                "Como você deseja proceder?",
                choices=[
                    questionary.Choice("[1] Ver instruções de instalação no terminal", value="instructions"),
                    questionary.Choice("[2] Abrir página de download no navegador", value="browser"),
                    menu_separator(),
                    questionary.Choice("[0] Voltar ao menu principal", value="exit"),
                    menu_footer(),
                ],
                **menu_options(),
            )
        except KeyboardInterrupt:
            return False

        if not choice or choice == "exit":
            return False
        if choice == "instructions":
            show_installation_instructions(dep_key)
        elif choice == "browser":
            open_download_page(dep_key)


def show_docker_daemon_guard() -> bool:
    """Exibe o guard quando o executável do Docker existe, mas o daemon está inativo."""
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "DOCKER", "SERVIÇO INATIVO"])
        typer.echo()
        message(
            "AVISO",
            "O executável do Docker foi encontrado, mas o daemon/serviço não está respondendo.",
            details=(
                "O Docker precisa do seu serviço em execução para exportar e importar imagens.\n"
                "Inicie o Docker Desktop (Windows/macOS) ou o serviço dockerd (Linux)."
            ),
        )
        typer.echo()

        try:
            choice = prompt(
                questionary.select,
                "Como você deseja proceder?",
                choices=[
                    questionary.Choice("[1] Tentar novamente", value="retry"),
                    questionary.Choice("[2] Ver orientações para iniciar o serviço", value="instructions"),
                    menu_separator(),
                    questionary.Choice("[0] Voltar ao menu principal", value="exit"),
                    menu_footer(),
                ],
                **menu_options(),
            )
        except KeyboardInterrupt:
            return False

        if not choice or choice == "exit":
            return False

        if choice == "retry":
            from utility_belt.doctor import check_docker

            res = check_docker()
            if res.get("daemon_running"):
                return True
            clear_screen()
            render_header(["UTILITY BELT", "DOCKER", "SERVIÇO INATIVO"])
            typer.echo()
            message("ERRO", "O daemon do Docker ainda não está acessível.")
            typer.echo()
            if sys.stdin.isatty():
                try:
                    questionary.press_any_key_to_continue(
                        "Pressione qualquer tecla para voltar...", style=menu_style()
                    ).ask()
                except (KeyboardInterrupt, EOFError):
                    pass

        elif choice == "instructions":
            clear_screen()
            render_header(["UTILITY BELT", "DOCKER", "INICIAR SERVIÇO"])
            typer.echo()
            if sys.platform == "win32":
                instructions = (
                    "No Windows:\n"
                    "  1. Abra o menu Iniciar e pesquise por 'Docker Desktop'.\n"
                    "  2. Inicie o aplicativo e aguarde o ícone da baleia na barra de tarefas estabilizar.\n"
                    "  3. Retorne ao Utility Belt e selecione 'Tentar novamente'."
                )
            else:
                instructions = (
                    "No Linux:\n"
                    "  1. Inicie o serviço com: sudo systemctl start docker\n"
                    "  2. Verifique o status com: sudo systemctl status docker\n"
                    "  3. Retorne ao Utility Belt e selecione 'Tentar novamente'."
                )
            message("INFO", "Como iniciar o Docker:", details=instructions)
            typer.echo()
            if sys.stdin.isatty():
                try:
                    questionary.press_any_key_to_continue(
                        "Pressione qualquer tecla para voltar...", style=menu_style()
                    ).ask()
                except (KeyboardInterrupt, EOFError):
                    pass


def ensure_dependency(dep_key: str) -> bool:
    """Ponto de entrada do preflight guard. Retorna True se apto a prosseguir, False para voltar ao menu."""
    if not sys.stdin.isatty():
        if not check_dependency_installed(dep_key):
            info = DEPENDENCY_INFO.get(dep_key, {})
            name = info.get("name", dep_key)
            print(f"Erro: Dependência '{name}' não está instalada ou não está no PATH.", file=sys.stderr)
            return False
        return True

    if dep_key == "restic":
        if not check_dependency_installed("restic"):
            return show_dependency_guard("restic")
        return True

    if dep_key == "docker":
        if not check_dependency_installed("docker"):
            return show_dependency_guard("docker")
        from utility_belt.doctor import check_docker

        docker_status = check_docker()
        if not docker_status.get("daemon_running"):
            return show_docker_daemon_guard()
        return True

    return True
