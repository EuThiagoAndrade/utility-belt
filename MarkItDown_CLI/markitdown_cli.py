import os
import sys
import subprocess
import argparse
import re
import json
import msvcrt
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.theme import Theme

# Configuração de tema para a interface
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "header": "bold white",
    "menu_opt": "white",
    "selected": "bold white on blue",
    "status": "white on blue"
})

console = Console(theme=custom_theme)

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
    console.print("\n[warning]🔍 MarkItDown não localizado automaticamente.[/warning]")
    path = console.input("[info]Digite o caminho completo do executável: [/info]").strip('"').strip("'").strip()
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
    console.print(f"[info]🔄 Processando: {input_path if is_url else input_path.name} ...[/info]")
    
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
            console.print(f"[success]✅ Sucesso: {output_path}[/success]")
            return True
        else:
            # Erros também podem ter caracteres especiais
            try:
                err_msg = result.stderr.decode('utf-8')
            except:
                err_msg = result.stderr.decode('cp1252', errors='replace')
            console.print(f"[danger]❌ Erro: {err_msg}[/danger]")
            return False
    except Exception as e:
        console.print(f"[danger]❌ Erro inesperado: {e}[/danger]")
        return False

def set_output_dir():
    """Configura a pasta de saída padrão."""
    console.print("\n[header]📂 Configurar Pasta de Saída Padrão[/header]")
    console.print("[menu_opt]Deixe em branco para salvar sempre na pasta do arquivo original.[/menu_opt]")
    path = console.input("[info]Caminho da pasta: [/info]").strip('"').strip("'").strip()
    
    config = load_config()
    if not path:
        config["output_dir"] = None
        console.print("[success]✅ Pasta padrão removida. Salvando arquivos na origem.[/success]")
    else:
        out_path = Path(path)
        out_path.mkdir(parents=True, exist_ok=True)
        config["output_dir"] = str(out_path)
        console.print(f"[success]✅ Pasta de saída configurada: {out_path}[/success]")
    
    save_config(config)

def draw_header():
    """Desenha o cabeçalho estilo terminal da imagem."""
    header = Text()
    header.append("terminal", style="success")
    header.append(" MarkItDown CLI v1.0", style="header")
    
    # Botões simulados (bolinhas do macOS/Windows Terminal)
    buttons = Text("  ○ ○ ○", style="dim white")
    
    # Criamos uma tabela invisível para alinhar o título e os botões
    header_table = Table.grid(expand=True)
    header_table.add_column(justify="left")
    header_table.add_column(justify="right")
    header_table.add_row(header, buttons)
    
    console.print(Panel(header_table, style="on grey15", padding=(0, 1)))

def draw_status_bar():
    """Desenha a barra de status inferior com créditos do desenvolvedor."""
    status = Text(" CLI - Desenvolvido por: THIAGO ANDRADE  |  https://github.com/EuThiagoAndrade ", style="bold white")
    
    # Tabela azul que ocupa toda a largura para centralizar o texto
    status_table = Table.grid(expand=True)
    status_table.add_column(justify="center")
    status_table.add_row(status)
    
    console.print(status_table, style="on blue")

def show_menu(exe_path):
    """Menu interativo com navegação por setas e interface Rich."""
    options = [
        "1. Converter Arquivo Único para Markdown",
        "2. Converter Pasta Inteira para Markdown (Lote)",
        "3. Converter URL (Web/YouTube) para Markdown",
        "4. Limpeza de Metadados YAML",
        "5. Definir Pasta de Saída Padrão",
        "6. Redefinir Localização do MarkItDown",
        "0. Sair do Programa"
    ]
    
    selected_index = 0
    remove_header = True
    
    while True:
        config = load_config()
        out_dir = config.get("output_dir", "Mesma pasta da origem")
        
        console.clear()
        draw_header()
        
        console.print("\n[header]MarkItDown - Conversor Universal para Markdown[/header]")
        console.print("[menu_opt]Use as setas [bold]↑ ↓[/bold] para navegar e [bold]Enter[/bold] para selecionar.[/menu_opt]\n")

        # Renderização das Opções
        for i, option in enumerate(options):
            style = "selected" if i == selected_index else "menu_opt"
            prefix = " > " if i == selected_index else "   "
            
            line = Text(f"{prefix}{option}", style=style)
            
            if "4. Limpeza" in option:
                status_text = Text.from_markup("[bold green] [ ATIVADA ][/bold green]" if remove_header else "[bold red] [ DESATIVADA ][/bold red]")
                line.append(status_text)
            
            console.print(line)
        
        console.print("\n" + "─" * 60, style="dim white")
        console.print(f" [info]Saída:[/info] [white]{out_dir}[/white]\n")
        
        draw_status_bar()

        # Prompt visualmente informativo logo abaixo da barra
        console.print("\n [bold blue]➜[/bold blue] [bold white]Escolha:[/bold white] ", end="")
        
        # Captura de tecla no Windows
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Tecla especial (setas)
            key = msvcrt.getch()
            if key == b'H':  # Seta para Cima
                selected_index = (selected_index - 1) % len(options)
            elif key == b'P':  # Seta para Baixo
                selected_index = (selected_index + 1) % len(options)
            continue
        
        if key == b'\r':  # Tecla Enter
            opcao_escolhida = options[selected_index].split('.')[0].strip()
        elif key.isdigit():
            opcao_escolhida = key.decode()
        else:
            continue

        # Lógica das opções
        if opcao_escolhida == '1':
            path = console.input("\n[info]Digite o caminho do Arquivo: [/info]").strip('"').strip("'")
            if path:
                convert_file(exe_path, path, remove_header=remove_header)
                console.input("\n[dim]Pressione Enter para voltar...[/dim]")
        elif opcao_escolhida == '2':
            path = console.input("\n[info]Digite o caminho da Pasta: [/info]").strip('"').strip("'")
            if path:
                process_directory(exe_path, Path(path), remove_header)
                console.input("\n[dim]Pressione Enter para voltar...[/dim]")
        elif opcao_escolhida == '3':
            url = console.input("\n[info]Digite a URL (Web/YouTube): [/info]").strip()
            if url:
                convert_file(exe_path, url, remove_header=remove_header)
                console.input("\n[dim]Pressione Enter para voltar...[/dim]")
        elif opcao_escolhida == '4':
            remove_header = not remove_header
        elif opcao_escolhida == '5':
            set_output_dir()
            console.input("\n[dim]Pressione Enter para voltar...[/dim]")
        elif opcao_escolhida == '6':
            if CONFIG_FILE.exists(): os.remove(CONFIG_FILE)
            console.print("[warning]Configurações redefinidas. Saindo...[/warning]")
            sys.exit(0)
        elif opcao_escolhida == '0':
            break

def process_directory(exe_path, input_path, remove_header):
    """Processa diretório."""
    if not input_path.is_dir():
        console.print("[danger]❌ Pasta inválida.[/danger]")
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
