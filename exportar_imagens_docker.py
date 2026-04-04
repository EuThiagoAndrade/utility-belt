import subprocess
import sys
from datetime import datetime

def main():
    # Força saída UTF-8 no Windows
    sys.stdout.reconfigure(encoding='utf-8')

    print("===================================================")
    print("  EXPORTADOR DE IMAGENS DOCKER")
    print("===================================================\n")

    # Nome do arquivo com a data atual
    hoje = datetime.now()
    nome_arquivo = f"imagens_para_casa_{hoje.day:02d}_{hoje.month:02d}_{hoje.year}.tar"

    # Quantidade de imagens
    while True:
        qtd_str = input("Quantas imagens voce deseja exportar? ").strip()
        if qtd_str.isdigit() and int(qtd_str) > 0:
            qtd = int(qtd_str)
            break
        print("\nOpcao invalida! Digite um numero inteiro maior que zero.\n")

    # Coleta os nomes/IDs das imagens
    print()
    imagens = []
    for i in range(1, qtd + 1):
        img = input(f"Digite o nome ou ID da imagem {i} de {qtd}: ").strip()
        imagens.append(img)

    # Exporta as imagens
    print(f"\nEmpacotando {qtd} imagem(ns) no arquivo '{nome_arquivo}'...")
    print("Isso pode demorar alguns minutos, aguarde.\n")

    comando = ["docker", "save", "-o", nome_arquivo] + imagens

    resultado = subprocess.run(comando)

    if resultado.returncode != 0:
        print("\nERRO! Algo deu errado durante a exportacao.")
        print("Verifique se os nomes/IDs das imagens estao corretos e tente novamente.")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    print()
    print("===================================================")
    print(f" Sucesso! Arquivo '{nome_arquivo}' gerado com {qtd} imagem(ns).")
    print(" Pode copiar o arquivo para o seu pen drive!")
    print("===================================================\n")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()