#!/usr/bin/env python3
"""Exportador seguro de imagens Docker com salvaguarda atômica."""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def listar_imagens_docker() -> list[str] | None:
    """Consulta as imagens disponíveis no daemon Docker."""
    try:
        resultado = subprocess.run(
            ["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        print("Erro: O executável 'docker' não foi encontrado no PATH.", file=sys.stderr)
        return None

    if resultado.returncode != 0:
        print(f"Erro ao listar imagens Docker:\n{resultado.stderr.strip()}", file=sys.stderr)
        return None

    imagens: list[str] = []
    for linha in resultado.stdout.splitlines():
        img = linha.strip()
        if img and "<none>" not in img and img not in imagens:
            imagens.append(img)
    return imagens


def selecionar_imagens_interativo(imagens: list[str]) -> list[str] | None:
    """Fluxo interativo no terminal para seleção de imagens."""
    if not imagens:
        print("Nenhuma imagem Docker disponível para exportar.")
        return None

    print("\nImagens Docker disponíveis:")
    for idx, img in enumerate(imagens, start=1):
        print(f"  {idx} - {img}")

    opcao_todas = len(imagens) + 1
    print(f"  {opcao_todas} - TODAS")
    print("  0 - Sair\n")

    while True:
        try:
            resposta = input("Qual imagem deseja exportar? (ex.: 1, 1 A 3, ou todas): ").strip().casefold()
        except (KeyboardInterrupt, EOFError):
            return None

        if resposta in {"0", "sair", "exit"}:
            return None
        if resposta in {"todas", "todos", str(opcao_todas)}:
            return imagens

        partes = resposta.replace("a", " ").split()
        if len(partes) == 1 and partes[0].isdigit():
            inicio = fim = int(partes[0])
        elif len(partes) == 2 and all(p.isdigit() for p in partes):
            inicio, fim = map(int, partes)
        else:
            print("Opção inválida. Digite um número, intervalo (ex.: 1 A 2) ou 'todas'.")
            continue

        if 1 <= inicio <= fim <= len(imagens):
            return imagens[inicio - 1 : fim]
        print("Número fora do intervalo da lista.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporta imagens Docker para arquivo .tar")
    parser.add_argument("--image", "-i", action="append", dest="images", help="Nome da imagem (ex.: alpine:latest). Pode ser usado múltiplas vezes.")
    parser.add_argument("--all", action="store_true", help="Exporta todas as imagens disponíveis.")
    parser.add_argument("--output", "-o", type=Path, help="Caminho do arquivo .tar ou pasta de saída.")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula a operação sem gravar o arquivo.")
    return parser.parse_args()


def main() -> int:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = parse_args()
    imagens_selecionadas: list[str] | None = args.images

    # Se não passou flag de imagem nem --all, avalia se pode rodar interativo
    if not imagens_selecionadas and not args.all:
        if not sys.stdin.isatty():
            print("Erro: Nenhuma imagem informada e terminal não interativo. Use --image ou --all.", file=sys.stderr)
            return 2

        disponiveis = listar_imagens_docker()
        if disponiveis is None:
            return 1
        imagens_selecionadas = selecionar_imagens_interativo(disponiveis)
        if not imagens_selecionadas:
            print("Operação cancelada pelo usuário.")
            return 0
    elif args.all:
        disponiveis = listar_imagens_docker()
        if disponiveis is None:
            return 1
        imagens_selecionadas = disponiveis

    if not imagens_selecionadas:
        print("Nenhuma imagem selecionada para exportação.", file=sys.stderr)
        return 1

    # Define o caminho de saída
    now = datetime.now()
    nome_padrao = f"imagens_exportadas_{now:%Y-%m-%d_%H-%M-%S}.tar"

    if args.output:
        out_path = args.output.resolve()
        if out_path.is_dir():
            target_tar = out_path / nome_padrao
        else:
            if out_path.suffix.lower() != ".tar":
                target_tar = out_path.with_suffix(".tar")
            else:
                target_tar = out_path
    else:
        target_tar = Path.cwd() / nome_padrao

    target_manifest = target_tar.with_suffix(".txt")
    temp_tar = target_tar.with_name(f"{target_tar.stem}.tmp.tar")

    print(f"\nPreparando exportação de {len(imagens_selecionadas)} imagem(ns):")
    for img in imagens_selecionadas:
        print(f"  - {img}")
    print(f"Destino final: {target_tar}")

    if args.dry_run:
        print("\n[DRY-RUN] Simulação concluída com sucesso. Nenhum arquivo foi gerado.")
        return 0

    target_tar.parent.mkdir(parents=True, exist_ok=True)

    # Executa a exportação gravando no arquivo temporário
    cmd = ["docker", "save", "-o", str(temp_tar)] + imagens_selecionadas
    print("\nExecutando docker save... (aguarde)")

    try:
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            print(f"\nErro no docker save (código {proc.returncode}). Limpando temporários.", file=sys.stderr)
            if temp_tar.exists():
                temp_tar.unlink()
            return proc.returncode

        # Promoção atômica do arquivo temporário para o destino final
        temp_tar.replace(target_tar)

        # Gravação do manifesto com lista de imagens
        manifest_content = (
            f"# Utility Belt - Manifesto de Imagens Docker\n"
            f"# Data: {now.isoformat()}\n"
            f"# Arquivo: {target_tar.name}\n\n"
            + "\n".join(imagens_selecionadas)
            + "\n"
        )
        target_manifest.write_text(manifest_content, encoding="utf-8")

        print(f"\nSucesso! Arquivo '{target_tar.name}' gerado.")
        print(f"Manifesto salvo em '{target_manifest.name}'.")
        return 0
    except KeyboardInterrupt:
        print("\nCancelado pelo usuário durante a exportação. Limpando temporários...", file=sys.stderr)
        if temp_tar.exists():
            temp_tar.unlink()
        return 130
    except Exception as err:
        print(f"\nFalha inesperada durante a exportação: {err}", file=sys.stderr)
        if temp_tar.exists():
            temp_tar.unlink()
        return 1


if __name__ == "__main__":
    sys.exit(main())
