import subprocess
import sys
from datetime import datetime
from pathlib import Path


def listar_imagens():
    try:
        resultado = subprocess.run(
            ["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        print("\nERRO! O Docker nao foi encontrado. Instale-o ou verifique se esta no PATH.")
        return None

    if resultado.returncode != 0:
        print("\nERRO! Nao foi possivel listar as imagens Docker.")
        if resultado.stderr.strip():
            print(resultado.stderr.strip())
        return None

    imagens = []
    for linha in resultado.stdout.splitlines():
        imagem = linha.strip()
        if imagem and "<none>" not in imagem and imagem not in imagens:
            imagens.append(imagem)

    return imagens


def selecionar_imagens(imagens):
    print("Imagens Docker disponiveis:\n")
    for indice, imagem in enumerate(imagens, start=1):
        print(f"{indice} - {imagem}")

    opcao_todas = len(imagens) + 1
    print(f"{opcao_todas} - TODAS")
    print("0 - SAIR\n")
    print("Como selecionar:")
    print("  Uma imagem: 2")
    print("  Um intervalo: 1 A 3 (inclui as imagens 1, 2 e 3)")
    print(f"  Todas: digite 'todas' ou {opcao_todas}")
    print("  Sair sem gerar arquivo: digite 'sair' ou 0\n")

    while True:
        resposta = input("Qual imagem deseja incluir? (ex.: 1 A 3 ou todas): ").strip()
        resposta_normalizada = resposta.casefold()

        if resposta_normalizada in {"0", "sair"}:
            return None

        if resposta_normalizada in {"todas", "todos"} or resposta == str(opcao_todas):
            return imagens

        partes = resposta_normalizada.replace("a", " ").split()
        if len(partes) == 1 and partes[0].isdigit():
            inicio = fim = int(partes[0])
        elif len(partes) == 2 and all(parte.isdigit() for parte in partes):
            inicio, fim = map(int, partes)
        else:
            print("\nOpcao invalida! Informe um numero, um intervalo como '1 A 2' ou 'todas'.\n")
            continue

        if 1 <= inicio <= fim <= len(imagens):
            return imagens[inicio - 1:fim]

        print("\nOpcao invalida! Escolha numeros exibidos na lista ou 'todas'.\n")


def selecionar_pasta_saida():
    while True:
        pasta = input("Pasta de saida (Enter para usar a pasta atual): ").strip().strip('"')
        if not pasta:
            return Path.cwd()

        caminho = Path(pasta).expanduser()
        if caminho.is_dir():
            return caminho

        print("\nPasta invalida ou inexistente. Informe um caminho de pasta valido.\n")


def main():
    # Força saída UTF-8 no Windows
    sys.stdout.reconfigure(encoding='utf-8')

    print("===================================================")
    print("  EXPORTADOR DE IMAGENS DOCKER")
    print("===================================================\n")

    imagens_disponiveis = listar_imagens()
    if imagens_disponiveis is None:
        input("\nPressione Enter para sair...")
        sys.exit(1)

    if not imagens_disponiveis:
        print("\nNenhuma imagem Docker com nome e tag foi encontrada.")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    print()
    imagens = selecionar_imagens(imagens_disponiveis)
    if imagens is None:
        print("\nOperacao cancelada. Nenhum arquivo foi gerado.")
        return

    qtd = len(imagens)
    pasta_saida = selecionar_pasta_saida()

    # ':' nao pode ser usado em nomes de arquivos no Windows.
    data_geracao = datetime.now()
    nome_base = f"imagens_exportadas_{data_geracao:%y-%m-%d_%H-%M-%S}"
    nome_arquivo = f"{nome_base}.tar"
    nome_manifesto = f"{nome_base}.txt"
    caminho_arquivo = pasta_saida / nome_arquivo
    caminho_manifesto = pasta_saida / nome_manifesto

    if caminho_arquivo.exists() or caminho_manifesto.exists():
        print(f"\nERRO! Ja existe um arquivo com o nome '{nome_base}' na pasta escolhida.")
        print("Aguarde um segundo e execute o script novamente.")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    # Exporta as imagens
    print(f"\nEmpacotando {qtd} imagem(ns) no arquivo '{nome_arquivo}'...")
    print("Isso pode demorar alguns minutos, aguarde.\n")

    comando = ["docker", "save", "-o", str(caminho_arquivo)] + imagens

    resultado = subprocess.run(comando)

    if resultado.returncode != 0:
        print("\nERRO! Algo deu errado durante a exportacao.")
        print("Verifique se os nomes das imagens estao corretos e tente novamente.")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    caminho_manifesto.write_text("\n".join(imagens) + "\n", encoding="utf-8")

    print()
    print("===================================================")
    print(f" Sucesso! Arquivo '{caminho_arquivo}' gerado com {qtd} imagem(ns).")
    print(f" Lista de imagens salva em '{caminho_manifesto}'.")
    print(" Pode copiar o arquivo para o seu pen drive!")
    print("===================================================\n")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
