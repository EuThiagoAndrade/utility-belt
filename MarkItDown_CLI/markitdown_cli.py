import os
import sys
import subprocess
import argparse
import re
import json
from pathlib import Path

# Arquivo de configuração persistente
CONFIG_FILE = Path(__file__).parent / "markitdown_config.json"

def load_config():
    """Carrega as configurações do arquivo JSON."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Salva as configurações no arquivo JSON."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def get_markitdown_path():
    """Localiza o executável do MarkItDown."""
    config = load_config()
    path = config.get("path")
    
    if path and os.path.exists(path):
        return path

    # Tenta encontrar no PATH
    try:
        cmd = 'where' if os.name == 'nt' else 'which'
        result = subprocess.run([cmd, 'markitdown'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass

    # Tenta encontrar em venvs locais
    for base_dir in [Path(__file__).parent, Path.cwd()]:
        for venv_name in ['.venv', 'venv']:
            suffix = "Scripts/markitdown.exe" if os.name == 'nt' else "bin/markitdown"
            candidate = base_dir / venv_name / suffix
            if candidate.exists():
                return str(candidate)
    return None

def setup_interactive_path():
    """Solicita o caminho do executável ao usuário."""
    print("\n🔍 MarkItDown não localizado automaticamente.")
    path = input("Digite o caminho completo do executável: ").strip('"').strip("'").strip()
    if os.path.exists(path):
        config = load_config()
        config["path"] = path
        save_config(config)
        return path
    return None

def clean_header(content):
    """Remove o cabeçalho YAML."""
    pattern = r'^---\s*\n.*?\n---\s*\n'
    return re.sub(pattern, '', content, count=1, flags=re.DOTALL | re.MULTILINE)

def convert_file(exe_path, input_path, output_path=None, remove_header=True):
    """Converte um arquivo ou URL para Markdown com correção de encoding."""
    config = load_config()
    default_out_dir = config.get("output_dir")
    
    is_url = str(input_path).startswith(('http://', 'https://'))
    
    if not is_url:
        input_path = Path(input_path)
        if not input_path.exists():
            print(f"⚠️ Não encontrado: {input_path}")
            return False
        
        if not output_path:
            # Se houver pasta padrão, salva lá. Senão, salva na pasta do arquivo original.
            if default_out_dir and os.path.exists(default_out_dir):
                output_path = Path(default_out_dir) / input_path.with_suffix('.md').name
            else:
                output_path = input_path.with_suffix('.md')
    else:
        if not output_path:
            if default_out_dir and os.path.exists(default_out_dir):
                output_path = Path(default_out_dir) / "web_content.md"
            else:
                output_path = Path("web_content.md")

    output_path = Path(output_path)
    print(f"🔄 Processando: {input_path if is_url else input_path.name} ...")
    
    try:
        # BUG FIX: Para resolver caracteres corrompidos no Windows,
        # capturamos a saída bruta (bytes) e tentamos decodificar com fallback.
        result = subprocess.run(
            [exe_path, str(input_path)],
            capture_output=True,
            check=False
        )
        
        if result.returncode == 0:
            # Tenta decodificar: UTF-8 primeiro, depois CP1252 (Windows Latin-1)
            try:
                content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                content = result.stdout.decode('cp1252', errors='replace')
            
            if remove_header:
                content = clean_header(content)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Sucesso: {output_path}")
            return True
        else:
            # Erros também podem ter caracteres especiais
            try:
                err_msg = result.stderr.decode('utf-8')
            except:
                err_msg = result.stderr.decode('cp1252', errors='replace')
            print(f"❌ Erro: {err_msg}")
            return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def set_output_dir():
    """Configura a pasta de saída padrão."""
    print("\n📂 Configurar Pasta de Saída Padrão")
    print("Deixe em branco para salvar sempre na pasta do arquivo original.")
    path = input("Caminho da pasta: ").strip('"').strip("'").strip()
    
    config = load_config()
    if not path:
        config["output_dir"] = None
        print("✅ Pasta padrão removida. Salvando arquivos na origem.")
    else:
        out_path = Path(path)
        out_path.mkdir(parents=True, exist_ok=True)
        config["output_dir"] = str(out_path)
        print(f"✅ Pasta de saída configurada: {out_path}")
    
    save_config(config)

def show_menu(exe_path):
    """Menu interativo."""
    remove_header = True
    while True:
        config = load_config()
        out_dir = config.get("output_dir", "Mesma pasta da origem")
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*60)
        print("🚀 MARKITDOWN CLI - VERSÃO CORRIGIDA")
        print(f"Motor: {exe_path}")
        print(f"Saída: {out_dir}")
        print("="*60)
        print("1. Converter Arquivo Único")
        print("2. Converter Pasta (Lote)")
        print("3. Converter URL (YouTube ou Site)")
        print("-" * 60)
        print(f"4. Opção: [ {'REMOVER' if remove_header else 'MANTER'} ] Cabeçalho YAML")
        print("5. Definir pasta de saída padrão")
        print("6. Redefinir caminho do MarkItDown")
        print("-" * 60)
        print("0. Sair")
        print("="*60)
        
        opcao = input("\nEscolha: ")
        if opcao == '1':
            path = input("Arquivo: ").strip('"').strip("'")
            convert_file(exe_path, path, remove_header=remove_header)
            input("\nEnter...")
        elif opcao == '2':
            path = input("Pasta: ").strip('"').strip("'")
            process_directory(exe_path, Path(path), remove_header)
            input("\nEnter...")
        elif opcao == '3':
            url = input("URL: ").strip()
            convert_file(exe_path, url, remove_header=remove_header)
            input("\nEnter...")
        elif opcao == '4':
            remove_header = not remove_header
        elif opcao == '5':
            set_output_dir()
            input("\nEnter...")
        elif opcao == '6':
            if CONFIG_FILE.exists(): os.remove(CONFIG_FILE)
            sys.exit(0)
        elif opcao == '0':
            break

def process_directory(exe_path, input_path, remove_header):
    """Processa diretório."""
    if not input_path.is_dir():
        print("❌ Pasta inválida.")
        return
    exts = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', 
            '.jpg', '.png', '.mp3', '.wav', '.html', '.htm', '.csv', 
            '.json', '.xml', '.epub', '.zip', '.msg']
    files = [f for f in input_path.glob("*.*") if f.suffix.lower() in exts]
    for f in files:
        convert_file(exe_path, f, remove_header=remove_header)

def main():
    parser = argparse.ArgumentParser(description="MarkItDown Fix & Improve")
    parser.add_argument("input", nargs="?", help="Arquivo ou URL")
    parser.add_argument("-o", "--output", help="Saída")
    parser.add_argument("-d", "--directory", action="store_true", help="Modo diretório")
    parser.add_argument("--keep-header", action="store_true", help="Mantém cabeçalho")
    
    args = parser.parse_args()
    exe_path = get_markitdown_path()
    if not exe_path:
        exe_path = setup_interactive_path()
        if not exe_path: sys.exit(1)

    if not args.input:
        show_menu(exe_path)
    else:
        remove_header = not args.keep_header
        if args.directory or Path(args.input).is_dir():
            process_directory(exe_path, Path(args.input), remove_header)
        else:
            convert_file(exe_path, args.input, args.output, remove_header)

if __name__ == "__main__":
    main()
