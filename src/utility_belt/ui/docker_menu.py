"""Menu interativo do Docker com navegação por setas (questionary)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import questionary
import typer

from utility_belt.config import load_config, save_config


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
        typer.secho(f"Erro ao listar imagens Docker: {e}", fg=typer.colors.RED)
        return []
    except FileNotFoundError:
        typer.secho("Docker não está instalado ou não está no PATH.", fg=typer.colors.RED)
        return []

def export_images() -> None:
    """Interactive flow to export Docker images."""
    typer.secho("\n--- Exportar Imagens Docker ---", fg=typer.colors.CYAN, bold=True)
    images = get_docker_images()

    if not images:
        typer.secho("Nenhuma imagem Docker encontrada.", fg=typer.colors.YELLOW)
        return

    selected_images = questionary.checkbox(
        "Selecione as imagens que deseja exportar (Espaço para selecionar, Enter para confirmar):",
        choices=images
    ).ask()

    if not selected_images:
        typer.secho("Nenhuma imagem selecionada. Operação cancelada.", fg=typer.colors.YELLOW)
        return

    config = load_config()
    last_dir = config.get("last_docker_export_dir", os.getcwd())

    output_dir_str = questionary.path(
        "Diretório de saída (Tab para autocompletar):",
        default=last_dir,
        only_directories=True
    ).ask()

    if not output_dir_str:
        typer.secho("Operação cancelada.", fg=typer.colors.YELLOW)
        return

    output_dir = Path(output_dir_str).resolve()

    if not output_dir.exists():
        create = questionary.confirm(f"Diretório '{output_dir}' não existe. Criar?").ask()
        if create:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                typer.secho(f"Erro ao criar diretório: {e}", fg=typer.colors.RED)
                return
        else:
            typer.secho("Operação cancelada.", fg=typer.colors.YELLOW)
            return

    config["last_docker_export_dir"] = str(output_dir)
    save_config(config)

    file_name = questionary.text(
        "Nome do arquivo de saída (sem a extensão .tar):",
        default="images_export"
    ).ask()

    if not file_name:
        typer.secho("Operação cancelada.", fg=typer.colors.YELLOW)
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

    typer.secho(f"\nExportando {len(raw_image_names)} imagem(ns) para {output_path}...", fg=typer.colors.BLUE)

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
        typer.secho(f"Imagens exportadas com sucesso para {output_path}!", fg=typer.colors.GREEN)
        typer.secho(f"Manifesto criado em {manifest_path}", fg=typer.colors.GREEN)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Erro ao exportar imagens: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Erro inesperado: {e}", fg=typer.colors.RED)


def import_images() -> None:
    """Interactive flow to import Docker images."""
    typer.secho("\n--- Importar Imagens Docker ---", fg=typer.colors.CYAN, bold=True)

    config = load_config()
    last_dir = config.get("last_docker_import_dir", os.getcwd())

    input_dir_str = questionary.path(
        "Diretório contendo os arquivos .tar (Tab para autocompletar):",
        default=last_dir,
        only_directories=True
    ).ask()

    if not input_dir_str:
        typer.secho("Operação cancelada.", fg=typer.colors.YELLOW)
        return

    input_dir = Path(input_dir_str).resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        typer.secho(f"Diretório '{input_dir}' inválido ou não encontrado.", fg=typer.colors.RED)
        return

    config["last_docker_import_dir"] = str(input_dir)
    save_config(config)

    tar_files = [f.name for f in input_dir.glob("*.tar")]

    if not tar_files:
        typer.secho(f"Nenhum arquivo .tar encontrado em {input_dir}.", fg=typer.colors.YELLOW)
        return

    selected_tar = questionary.select(
        "Selecione o arquivo para importar:",
        choices=tar_files
    ).ask()

    if not selected_tar:
        typer.secho("Nenhum arquivo selecionado. Operação cancelada.", fg=typer.colors.YELLOW)
        return

    tar_path = input_dir / selected_tar

    # Try to find and read manifest
    manifest_path = input_dir / f"{tar_path.stem}_manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            typer.secho("\nManifesto encontrado:", fg=typer.colors.BLUE)
            typer.secho(json.dumps(manifest_data, indent=2), fg=typer.colors.CYAN)

            confirm = questionary.confirm("Deseja prosseguir com a importação?").ask()
            if not confirm:
                typer.secho("Operação cancelada.", fg=typer.colors.YELLOW)
                return
        except Exception as e:
            typer.secho(f"Aviso: Não foi possível ler o manifesto: {e}", fg=typer.colors.YELLOW)

    typer.secho(f"\nCarregando imagens de {tar_path}...", fg=typer.colors.BLUE)

    try:
        result = subprocess.run(
            ["docker", "load", "-i", str(tar_path)],
            capture_output=True,
            text=True,
            check=True
        )
        typer.secho(result.stdout, fg=typer.colors.GREEN)
        typer.secho("Importação concluída com sucesso!", fg=typer.colors.GREEN, bold=True)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Erro ao importar imagens:\n{e.stderr}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Erro inesperado: {e}", fg=typer.colors.RED)


def show_docker_menu() -> None:
    """Main entry point for the interactive Docker menu."""
    while True:
        try:
            choice = questionary.select(
                "Menu Docker - O que você deseja fazer?",
                choices=[
                    questionary.Choice("Exportar imagens para .tar", "export"),
                    questionary.Choice("Importar imagens de um .tar", "import"),
                    questionary.Choice("Voltar / Sair", "exit")
                ]
            ).ask()

            if not choice or choice == "exit":
                typer.secho("Saindo do menu Docker...", fg=typer.colors.BLUE)
                break
            elif choice == "export":
                export_images()
            elif choice == "import":
                import_images()

            print() # Print empty line for better readability between actions
        except KeyboardInterrupt:
            typer.secho("\nOperação interrompida pelo usuário.", fg=typer.colors.YELLOW)
            break
        except Exception as e:
            typer.secho(f"\nErro inesperado no menu: {e}", fg=typer.colors.RED)
            break
