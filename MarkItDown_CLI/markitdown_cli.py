import os
import sys
import subprocess
import argparse
import re
import json
from pathlib import Path

# Arquivo de configuração persistente
CONFIG_FILE = Path(__file__).parent / "markitdown_config.json"

def get_markitdown_path():
    """
    Estado da Arte em Descoberta de Ferramentas:
    1. Verifica Configuração Salva.
    2. Verifica PATH do Sistema.
    3. Verifica Pastas de Ambiente Virtual Padrão (.venv, venv).
    4. Solicita ao usuário se falhar em tudo.
    """
    # 1. Configuração salva
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                path = config.get("path")
                if path and os.path.exists(path):
                    return path
        except:
            pass

    # 2. PATH do Sistema
    try:
        # No Windows, 'where' localiza executáveis no PATH
        cmd = 'where' if os.name == 'nt' else 'which'
        result = subprocess.run([cmd, 'markitdown'], capture_output=True, text=True)
        if result.returncode == 0:
            path = result.stdout.strip().split('\n')[0]
            return path
    except:
        pass

    # 3. Pastas Padrão de Venv (.venv ou venv)
    # Procura no diretório do script e no diretório onde o usuário está
    for base_dir in [Path(__file__).parent, Path.cwd()]:
        for venv_name in ['.venv', 'venv']:
            suffix = "Scripts/markitdown.exe" if os.name == 'nt' else "bin/markitdown"
            candidate = base_dir / venv_name / suffix
            if candidate.exists():
                return str(candidate)

    return None

def setup_interactive_path():
    """Solicita o caminho ao usuário e salva."""
    print("\n🔍 MarkItDown não foi localizado automaticamente.")
    print("Exemplos de caminhos:")
    print(r" - C:\Users\Nome\.venv\Scripts\markitdown.exe")
    print(r" - C:\Python312\Scripts\markitdown.exe")
    
    path = input("\nPor favor, digite o caminho completo do executável: ").strip('"').strip("'").strip()
    
    if os.path.exists(path) and (path.endswith('.exe') or os.name != 'nt'):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"path": path}, f)
        print("✅ Configuração salva com sucesso!")
        return path
    else:
        print("❌ Caminho inválido ou arquivo não encontrado.")
        return None

def clean_header(content):
    """Remove o cabeçalho YAML (front matter) do conteúdo Markdown."""
    pattern = r'^---\s*\n.*?\n---\s*\n'
    cleaned = re.sub(pattern, '', content, count=1, flags=re.DOTALL | re.MULTILINE)
    return cleaned

def convert_file(exe_path, input_path, output_path=None, remove_header=True):
    """Converte um arquivo ou URL para Markdown."""
    is_url = str(input_path).startswith(('http://', 'https://'))
    
    if not is_url:
        input_path = Path(input_path)
        if not input_path.exists():
            print(f"⚠️ Arquivo não encontrado: {input_path}")
            return False
        if not output_path:
            output_path = input_path.with_suffix('.md')
    else:
        if not output_path:
            output_path = Path("converted_content.md")
    
    output_path = Path(output_path)
    print(f"🔄 Processando: {input_path if is_url else input_path.name} ...")
    
    try:
        result = subprocess.run(
            [exe_path, str(input_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            content = result.stdout
            if remove_header:
                content = clean_header(content)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Sucesso: {output_path}")
            return True
        else:
            print(f"❌ Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def show_menu(exe_path):
    """Menu interativo."""
    remove_header = True
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*60)
        print("🚀 MARKITDOWN CLI - AMBIENTE DINÂMICO")
        print(f"Local: {exe_path}")
        print("="*60)
        print("1. Converter Arquivo Único")
        print("2. Converter Pasta (Lote)")
        print("3. Converter URL (YouTube ou Site)")
        print("-" * 60)
        print(f"4. Opção: [ {'REMOVER' if remove_header else 'MANTER'} ] Cabeçalho YAML")
        print("5. Redefinir caminho do MarkItDown")
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
            if CONFIG_FILE.exists(): os.remove(CONFIG_FILE)
            print("Configuração removida. O script será reiniciado.")
            sys.exit(0)
        elif opcao == '0':
            break

def process_directory(exe_path, input_path, remove_header):
    """Processa diretório em lote."""
    if not input_path.is_dir():
        print("❌ Diretório inválido.")
        return
    
    exts = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', 
            '.jpg', '.png', '.mp3', '.wav', '.html', '.htm', '.csv', 
            '.json', '.xml', '.epub', '.zip', '.msg']
    
    files = [f for f in input_path.glob("*.*") if f.suffix.lower() in exts]
    for f in files:
        convert_file(exe_path, f, remove_header=remove_header)

def main():
    parser = argparse.ArgumentParser(description="MarkItDown Dynamic CLI")
    parser.add_argument("input", nargs="?", help="Arquivo ou URL")
    parser.add_argument("-o", "--output", help="Saída")
    parser.add_argument("-d", "--directory", action="store_true", help="Modo diretório")
    parser.add_argument("--keep-header", action="store_true", help="Mantém cabeçalho")
    parser.add_argument("--set-path", help="Configura o caminho do executável manualmente")
    
    args = parser.parse_args()

    # Se o usuário passou o caminho via flag, salva e continua
    if args.set_path:
        if os.path.exists(args.set_path):
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({"path": args.set_path}, f)
            print(f"✅ Caminho configurado para: {args.set_path}")
        else:
            print("❌ Caminho fornecido não existe.")
            sys.exit(1)

    exe_path = get_markitdown_path()

    if not exe_path:
        exe_path = setup_interactive_path()
        if not exe_path:
            sys.exit(1)

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
