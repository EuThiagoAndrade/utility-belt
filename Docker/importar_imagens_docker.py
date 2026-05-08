import subprocess
import sys
import os
from pathlib import Path

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    print("===================================================")
    print("  IMPORTADOR DE IMAGENS DOCKER")
    print("===================================================\n")

    # ── 1. Localiza o arquivo .tar ──────────────────────────────────────────
    while True:
        caminho_str = input("Digite o caminho completo do arquivo .tar: ").strip().strip('"')
        caminho = Path(caminho_str)

        if not caminho.exists():
            print(f"\nArquivo '{caminho}' nao encontrado. Tente novamente.\n")
            continue
        if caminho.suffix.lower() != ".tar":
            print("\nO arquivo informado nao possui extensao .tar. Tente novamente.\n")
            continue
        break

    # ── 2. Carrega as imagens do .tar ───────────────────────────────────────
    print(f"\nCarregando imagens do arquivo '{caminho.name}'...")
    print("Aguarde, isso pode demorar alguns minutos.\n")

    resultado = subprocess.run(
        ["docker", "load", "-i", str(caminho)],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        print("ERRO ao carregar as imagens!")
        print(resultado.stderr)
        input("\nPressione Enter para sair...")
        sys.exit(1)

    # Extrai os nomes das imagens carregadas da saída do docker load
    # Ex: "Loaded image: minha-imagem:latest"
    imagens_carregadas = []
    for linha in resultado.stdout.splitlines():
        if linha.startswith("Loaded image"):
            nome = linha.split(":", 1)[-1].strip()
            imagens_carregadas.append(nome)
            print(f"  [OK] {nome}")

    if not imagens_carregadas:
        print("Nenhuma imagem foi identificada na saida do docker load.")
        print("Saida bruta:")
        print(resultado.stdout)
        input("\nPressione Enter para sair...")
        sys.exit(1)

    print(f"\n{len(imagens_carregadas)} imagem(ns) carregada(s) com sucesso!\n")

    # ── 3. Escolhe qual imagem executar (opcional) ──────────────────────────
    executar = input("Deseja executar uma imagem agora? (s/n): ").strip().lower()

    if executar != "s":
        print()
        print("===================================================")
        print(" Imagens importadas com sucesso. Nenhum container")
        print(" foi iniciado.")
        print("===================================================\n")
        input("Pressione Enter para sair...")
        return

    if len(imagens_carregadas) == 1:
        imagem_escolhida = imagens_carregadas[0]
        print(f"Imagem selecionada automaticamente: {imagem_escolhida}")
    else:
        print("Imagens disponiveis:")
        for i, img in enumerate(imagens_carregadas, 1):
            print(f"  [{i}] {img}")

        while True:
            escolha = input("\nDigite o numero da imagem que deseja executar: ").strip()
            if escolha.isdigit() and 1 <= int(escolha) <= len(imagens_carregadas):
                imagem_escolhida = imagens_carregadas[int(escolha) - 1]
                break
            print("Opcao invalida! Tente novamente.")

    # ── 4. Configurações do container (opcional) ─────────────────────────────
    print()
    configurar = input("Deseja configurar o container antes de executar? (s/n): ").strip().lower()

    porta = ""
    porta_container = ""
    nome_container = ""
    modo_daemon = "n"

    if configurar == "s":
        porta = input("Porta do HOST a mapear (ex: 8080) — pressione Enter para pular: ").strip()
        if porta:
            porta_container = input("Porta do CONTAINER correspondente (ex: 80): ").strip()

        nome_container = input("Nome para o container (pressione Enter para deixar o Docker escolher): ").strip()
        modo_daemon = input("Executar em segundo plano? (s/n): ").strip().lower()

    # ── 5. Monta e executa o comando docker run ──────────────────────────────
    comando = ["docker", "run"]

    if modo_daemon == "s":
        comando.append("-d")
    else:
        comando += ["-it", "--rm"]

    if porta and porta_container:
        comando += ["-p", f"{porta}:{porta_container}"]

    if nome_container:
        comando += ["--name", nome_container]

    comando.append(imagem_escolhida)

    print(f"\nExecutando: {' '.join(comando)}\n")
    resultado_run = subprocess.run(comando)

    if resultado_run.returncode != 0:
        print("\nERRO ao executar o container!")
        print("Verifique os parametros e tente novamente.")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    print()
    print("===================================================")
    print(f" Container iniciado com a imagem '{imagem_escolhida}'.")
    if nome_container:
        print(f" Nome do container: {nome_container}")
    if porta and porta_container:
        print(f" Porta mapeada: {porta} (host) -> {porta_container} (container)")
    print("===================================================\n")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()