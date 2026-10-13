"""Menu interativo do Docker com navegação por setas (questionary)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import questionary
import typer

from utility_belt.config import load_config, save_config
from utility_belt.ui.screen import (
    clear_screen,
    menu_footer,
    menu_options,
    menu_separator,
    prompt,
    render_header,
    run_dedicated_screen,
    status_message,
)


def get_docker_images() -> list[str]:
    """Retrieve a list of local Docker images."""
    try:
        result = subprocess.run(
            ["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}} ({{.Size}}, ID: {{.ID}})"],
            capture_output=True,
            text=True,
            check=True
        )
        images = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return images
    except subprocess.CalledProcessError as e:
        status_message(f"Erro ao listar imagens Docker: {e}", fg=typer.colors.RED)
        return []
    except FileNotFoundError:
        status_message("Docker não está instalado ou não está no PATH.", fg=typer.colors.RED)
        return []

def export_images() -> None:
    """Interactive flow to export Docker images."""
    status_message("\n--- Exportar Imagens Docker ---", fg=typer.colors.CYAN, bold=True)
    images = get_docker_images()

    if not images:
        status_message("Nenhuma imagem Docker encontrada.", fg=typer.colors.YELLOW)
        return

    selected_images = prompt(questionary.checkbox,
        "Selecione as imagens que deseja exportar (Espaço para selecionar, Enter para confirmar):",
        choices=images
    )

    if not selected_images:
        status_message("Nenhuma imagem selecionada. Operação cancelada.", fg=typer.colors.YELLOW)
        return

    config = load_config()
    last_dir = config.get("last_docker_export_dir", os.getcwd())

    output_dir_str = prompt(questionary.path,
        "Diretório de saída (Tab para autocompletar):",
        default=last_dir,
        only_directories=True
    )

    if not output_dir_str:
        status_message("Operação cancelada.", fg=typer.colors.YELLOW)
        return

    output_dir = Path(output_dir_str).resolve()

    if not output_dir.exists():
        create = prompt(questionary.confirm, f"Diretório '{output_dir}' não existe. Criar?")
        if create:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                status_message(f"Erro ao criar diretório: {e}", fg=typer.colors.RED)
                return
        else:
            status_message("Operação cancelada.", fg=typer.colors.YELLOW)
            return

    config["last_docker_export_dir"] = str(output_dir)
    save_config(config)

    file_name = prompt(questionary.text,
        "Nome do arquivo de saída (sem a extensão .tar):",
        default="images_export"
    )

    if not file_name:
        status_message("Operação cancelada.", fg=typer.colors.YELLOW)
        return

    if not file_name.endswith(".tar"):
        file_name += ".tar"

    output_path = output_dir / file_name

    # Extract only Repository:Tag
    raw_image_names = []
    for img in selected_images:
        # Example format: "ubuntu:latest (72.8MB, ID: 123456789abc)"
        repo_tag = img.split(" (")[0]
        raw_image_names.append(repo_tag)

    status_message(f"\nExportando {len(raw_image_names)} imagem(ns) para {output_path}...", fg=typer.colors.BLUE)

    try:
        # Create manifest
        manifest_path = output_dir / f"{output_path.stem}_manifest.json"
        manifest_data = {
            "images": raw_image_names,
            "export_file": output_path.name
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)

        cmd = ["docker", "save", "-o", str(output_path)] + raw_image_names
        subprocess.run(cmd, check=True)
        status_message(f"Imagens exportadas com sucesso para {output_path}!", fg=typer.colors.GREEN)
        status_message(f"Manifesto criado em {manifest_path}", fg=typer.colors.GREEN)
    except subprocess.CalledProcessError as e:
        status_message(f"Erro ao exportar imagens: {e}", fg=typer.colors.RED)
    except Exception as e:
        status_message(f"Erro inesperado: {e}", fg=typer.colors.RED)


def import_images() -> None:
    """Interactive flow to import Docker images."""
    status_message("\n--- Importar Imagens Docker ---", fg=typer.colors.CYAN, bold=True)

    config = load_config()
    last_dir = config.get("last_docker_import_dir", os.getcwd())

    input_dir_str = prompt(questionary.path,
        "Diretório contendo os arquivos .tar (Tab para autocompletar):",
        default=last_dir,
        only_directories=True
    )

    if not input_dir_str:
        status_message("Operação cancelada.", fg=typer.colors.YELLOW)
        return

    input_dir = Path(input_dir_str).resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        status_message(f"Diretório '{input_dir}' inválido ou não encontrado.", fg=typer.colors.RED)
        return

    config["last_docker_import_dir"] = str(input_dir)
    save_config(config)

    tar_files = [f.name for f in input_dir.glob("*.tar")]

    if not tar_files:
        status_message(f"Nenhum arquivo .tar encontrado em {input_dir}.", fg=typer.colors.YELLOW)
        return

    selected_tar = prompt(questionary.select,
        "Selecione o arquivo para importar:",
        choices=tar_files
    )

    if not selected_tar:
        status_message("Nenhum arquivo selecionado. Operação cancelada.", fg=typer.colors.YELLOW)
        return

    tar_path = input_dir / selected_tar

    # Try to find and read manifest
    manifest_path = input_dir / f"{tar_path.stem}_manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            status_message("\nManifesto encontrado:", fg=typer.colors.BLUE)
            status_message(json.dumps(manifest_data, indent=2), fg=typer.colors.CYAN)

            confirm = prompt(questionary.confirm, "Deseja prosseguir com a importação?")
            if not confirm:
                status_message("Operação cancelada.", fg=typer.colors.YELLOW)
                return
        except Exception as e:
            status_message(f"Aviso: Não foi possível ler o manifesto: {e}", fg=typer.colors.YELLOW)

    status_message(f"\nCarregando imagens de {tar_path}...", fg=typer.colors.BLUE)

    try:
        result = subprocess.run(
            ["docker", "load", "-i", str(tar_path)],
            capture_output=True,
            text=True,
            check=True
        )
        status_message(result.stdout, fg=typer.colors.GREEN)
        status_message("Importação concluída com sucesso!", fg=typer.colors.GREEN, bold=True)
    except subprocess.CalledProcessError as e:
        status_message(f"Erro ao importar imagens:\n{e.stderr}", fg=typer.colors.RED)
    except Exception as e:
        status_message(f"Erro inesperado: {e}", fg=typer.colors.RED)


def show_docker_menu() -> None:
    """Ponto de entrada principal para o menu interativo do Docker."""
    while True:
        clear_screen()
        render_header(["UTILITY BELT", "DOCKER"])
        typer.echo()
        try:
            choice = prompt(questionary.select,
                "Menu Docker — Escolha uma opção:",
                choices=[
                    questionary.Choice("[1] Exportar imagens para .tar", "export"),
                    questionary.Choice("[2] Importar imagens de um .tar", "import"),
                    menu_separator(),
                    questionary.Choice("[0] Voltar ao menu principal", "exit"),
                    menu_footer(),
                ],
                **menu_options(),
            )

            if not choice or choice == "exit":
                break
            elif choice == "export":
                run_dedicated_screen(["UTILITY BELT", "DOCKER", "EXPORTAR"], export_images)
            elif choice == "import":
                run_dedicated_screen(["UTILITY BELT", "DOCKER", "IMPORTAR"], import_images)

        except KeyboardInterrupt:
            break
        except Exception as e:
            status_message(f"\nErro inesperado no menu: {e}", fg=typer.colors.RED)
            break
