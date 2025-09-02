import os
import subprocess
from pathlib import Path

# 1. DEFINIR O ALVO E AS REGRAS DE ORGANIZAÇÃO
# Path.home() pega a pasta do usuário atual (ex: C:\Users\SeuNome)
# E então adicionamos "Downloads" para formar o caminho completo.
downloads_path = Path.home() / "Downloads"

# Dicionário que mapeia o nome da pasta para uma lista de extensões de arquivo.
# Sinta-se à vontade para adicionar mais extensões e pastas!
PASTAS_POR_TIPO = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documentos": [".docx", ".doc", ".txt", ".rtf", ".odt"],
    "PDFs": [".pdf"],
    "Aplicativos": [".exe", ".msi"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Planilhas": [".xlsx", ".xls", ".csv"],
    "Apresentacoes": [".pptx", ".ppt"],
}

# 2. FUNÇÃO PARA EXECUTAR COMANDOS POWERSHELL
def executar_powershell(command):
    """Função para chamar o PowerShell de forma segura."""
    try:
        # Executa o comando e espera ele terminar
        subprocess.run(["powershell", "-Command", command], check=True, capture_output=True, text=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        # Se o PowerShell retornar um erro, capturamos aqui
        print(f"Erro ao executar o comando: {command}")
        print(f"Erro do PowerShell: {e.stderr}")
        return False, e.stderr

# 3. LÓGICA PRINCIPAL DE ORGANIZAÇÃO
print(f"Iniciando organização da pasta: {downloads_path}")

# Itera sobre todos os arquivos e pastas dentro de Downloads
for item in os.scandir(downloads_path):
    # Ignora se não for um arquivo (ou seja, se for uma pasta)
    if not item.is_file():
        continue
    
    # Pega a extensão do arquivo em minúsculas (ex: ".jpg")
    extensao = Path(item.name).suffix.lower()
    pasta_destino = None

    # Verifica em qual pasta o arquivo deve ser movido
    for pasta, extensoes in PASTAS_POR_TIPO.items():
        if extensao in extensoes:
            pasta_destino = downloads_path / pasta
            break
    
    # Se o tipo de arquivo não estiver no nosso mapa, pula para o próximo
    if not pasta_destino:
        continue

    # 4. PYTHON CHAMA O POWERSHELL PARA AGIR
    print(f"Movendo '{item.name}' para a pasta '{pasta_destino.name}'...")
    
    # Comando 1: Cria a pasta de destino (não dá erro se ela já existir)
    comando_criar_pasta = f"New-Item -Path '{pasta_destino}' -ItemType Directory -Force | Out-Null"
    executar_powershell(comando_criar_pasta)
    
    # Comando 2: Move o arquivo para a pasta de destino
    comando_mover_arquivo = f"Move-Item -Path '{item.path}' -Destination '{pasta_destino}'"
    executar_powershell(comando_mover_arquivo)

print("Organização concluída com sucesso!")