#!/usr/bin/env python3
"""Importador seguro de imagens Docker com separação estrita de execução."""

import argparse
import subprocess
import sys
from pathlib import Path


def exibir_manifesto(caminho_tar: Path) -> None:
    """Verifica e exibe manifesto .txt auxiliar associado ao .tar."""
    manifesto = caminho_tar.with_suffix(".txt")
    if not manifesto.is_file():
        print("Aviso: Nenhum manifesto .txt correspondente encontrado.")
        return

    try:
        conteudo = manifesto.read_text(encoding="utf-8").strip()
        print(f"\nConteúdo do manifesto '{manifesto.name}':")
        print("---------------------------------------------------")
        print(conteudo if conteudo else "(manifesto vazio)")
        print("---------------------------------------------------")
    except Exception as err:
        print(f"Aviso: Falha ao ler manifesto '{manifesto.name}': {err}")


def selecionar_tar_interativo() -> Path | None:
    """Seleção interativa de arquivo .tar no terminal."""
    cwd = Path.cwd()
    tars = sorted(list(cwd.glob("*.tar")), key=lambda p: p.name.lower())

    if tars:
        print("\nArquivos .tar encontrados no diretório atual:")
        for idx, tar in enumerate(tars, start=1):
            print(f"  {idx} - {tar.name}")
        print("  0 - Informar outro caminho ou sair")

        try:
            escolha = input("\nEscolha o número do arquivo (ou 0 para digitar caminho): ").strip()
            if escolha.isdigit() and 1 <= int(escolha) <= len(tars):
                return tars[int(escolha) - 1]
        except (KeyboardInterrupt, EOFError):
            return None

    while True:
        try:
            resp = input("Digite o caminho do arquivo .tar (ou 'sair'): ").strip().strip('"')
        except (KeyboardInterrupt, EOFError):
            return None

        if resp.casefold() in {"0", "sair", "exit"}:
            return None

        p = Path(resp).expanduser()
        if p.is_file() and p.suffix.lower() == ".tar":
            return p
        print("Arquivo inválido ou não encontrado. Tente novamente.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Importa imagens Docker a partir de arquivo .tar")
    parser.add_argument("--input", "-i", type=Path, help="Caminho do arquivo .tar para importação.")
    parser.add_argument("--dry-run", action="store_true", help="Apenas valida o arquivo e exibe manifesto sem importar.")
    parser.add_argument("--run", action="store_true", help="Oferece iniciar um container interativamente após a importação.")
    return parser.parse_args()


def main() -> int:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = parse_args()
    caminho_tar: Path | None = args.input

    if not caminho_tar:
        if not sys.stdin.isatty():
            print("Erro: Nenhum arquivo informado e terminal não interativo. Use --input <arquivo.tar>.", file=sys.stderr)
            return 2

        caminho_tar = selecionar_tar_interativo()
        if not caminho_tar:
            print("Operação cancelada pelo usuário.")
            return 0

    caminho_tar = caminho_tar.resolve()
    if not caminho_tar.is_file():
        print(f"Erro: Arquivo '{caminho_tar}' não encontrado.", file=sys.stderr)
        return 1

    print(f"\nArquivo selecionado: {caminho_tar.name}")
    exibir_manifesto(caminho_tar)

    if args.dry_run:
        print("\n[DRY-RUN] Validação concluída com sucesso. Nenhuma imagem foi carregada no Docker.")
        return 0

    print(f"\nImportando imagens do arquivo '{caminho_tar.name}' via docker load...")
    try:
        proc = subprocess.run(
            ["docker", "load", "-i", str(caminho_tar)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        print("Erro: Executável 'docker' não encontrado no PATH.", file=sys.stderr)
        return 2

    if proc.returncode != 0:
        print(f"Erro no docker load (código {proc.returncode}):\n{proc.stderr}", file=sys.stderr)
        return proc.returncode

    # Processa e exibe as imagens carregadas
    imagens_carregadas: list[str] = []
    for linha in proc.stdout.splitlines():
        if "Loaded image" in linha:
            nome = linha.split(":", 1)[-1].strip()
            imagens_carregadas.append(nome)
            print(f"  [OK] {nome}")

    if not imagens_carregadas:
        print("Imagens carregadas (saída bruta):")
        print(proc.stdout)
    else:
        print(f"\nSucesso: {len(imagens_carregadas)} imagem(ns) importada(s).")

    # Execução opcional de container (somente se flag explícita --run)
    if args.run and sys.stdin.isatty() and imagens_carregadas:
        print("\n--- Execução Opcional de Container ---")
        try:
            quer_rodar = input("Deseja executar um container com uma dessas imagens agora? [s/N]: ").strip().lower()
            if quer_rodar in {"s", "sim"}:
                imagem_alvo = imagens_carregadas[0]
                if len(imagens_carregadas) > 1:
                    for i, img in enumerate(imagens_carregadas, 1):
                        print(f"  {i}. {img}")
                    idx_str = input("Número da imagem: ").strip()
                    if idx_str.isdigit() and 1 <= int(idx_str) <= len(imagens_carregadas):
                        imagem_alvo = imagens_carregadas[int(idx_str) - 1]

                cmd_run = ["docker", "run", "-it", "--rm", imagem_alvo]
                print(f"Executando: {' '.join(cmd_run)}\n")
                res_run = subprocess.run(cmd_run)
                return res_run.returncode
        except (KeyboardInterrupt, EOFError):
            print("\nExecução de container ignorada.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
