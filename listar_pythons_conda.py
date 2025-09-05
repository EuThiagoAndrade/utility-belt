#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def run_conda_info_json() -> Dict:
    """
    Executa 'conda info --json' e retorna o dicionário Python resultante.

    Por que usar --json?
        - É a forma mais confiável e estável de consumir a saída do Conda
          programaticamente (evita "parsear" texto de terminal).
    Tratamento de erros:
        - Se 'conda' não estiver no PATH ou o comando falhar, uma mensagem
          clara é exibida e o script encerra com código de erro.
    """
    try:
        # capture_output=True -> captura stdout/stderr
        # text=True -> retorna string (não bytes)
        # check=True -> lança exceção se o retorno do processo for != 0
        result = subprocess.run(
            ["conda", "info", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        # Erro típico quando o 'conda' não está disponível no PATH
        print(
            "Erro: 'conda' não foi encontrado no PATH.\n"
            "Abra o script pelo 'Anaconda Prompt' ou adicione o Conda ao PATH.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # Caso 'conda info --json' retorne código de erro, mostramos detalhes
        print(
            "Erro ao executar 'conda info --json'.\n"
            f"Saída de erro (stderr):\n{e.stderr}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # Converte a string JSON em dicionário Python
        data = json.loads(result.stdout)
        return data
    except json.JSONDecodeError as e:
        print(
            "Erro ao interpretar a saída JSON do 'conda info --json'.\n"
            f"Detalhes: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def collect_env_entries(info: Dict) -> List[Tuple[str, str]]:
    """
    A partir do dicionário retornado por 'conda info --json', monta a lista de
    (nome_do_ambiente, caminho_do_python).

    Detalhes importantes:
        - 'root_prefix' é o caminho do ambiente base (normalmente 'base').
        - 'envs' é uma lista de 'prefixos' (caminhos) para cada ambiente.
        - Para cada prefixo, deduzimos o caminho do executável Python:
            * Windows: <prefixo>/python.exe
            * Linux/macOS: <prefixo>/bin/python
        - O 'name' do ambiente:
            * 'base' se o prefixo == root_prefix
            * caso contrário, usamos o último nome do caminho (prefix.name)

    Retorno:
        Uma lista de tuplas (nome, caminho_python_ou_mensagem_de_nao_encontrado)
        ainda não ordenada.
    """
    # O 'root_prefix' identifica o ambiente 'base'
    root = Path(info.get("root_prefix", ""))

    # 'envs' é uma lista de caminhos (prefixos) dos ambientes
    env_paths = set(Path(p) for p in info.get("envs", []))

    # Garante que o ambiente base esteja na lista final
    if root:
        env_paths.add(root)

    entries: List[Tuple[str, str]] = []

    # Define o nome do executável conforme o SO
    exe_name = "python.exe" if os.name == "nt" else "bin/python"

    for prefix in env_paths:
        # Determina o "nome" para exibir:
        # - "base" se o prefixo for exatamente o root_prefix
        # - caso contrário, usa o nome da pasta do prefixo (prefix.name)
        name = "base" if (root and prefix == root) else prefix.name

        # Constrói o caminho absoluto para o executável Python do ambiente
        py_path = prefix / exe_name

        # Se o arquivo existir, usamos o caminho; caso contrário, sinalizamos
        if py_path.exists():
            display = str(py_path)
        else:
            display = f"{py_path} (não encontrado)"

        entries.append((name, display))

    return entries


def sort_entries(entries: Iterable[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Ordena a lista de (nome, caminho) colocando 'base' primeiro e
    o restante em ordem alfabética case-insensitive.

    Por que ordenar?
        - Deixa a saída previsível e amigável, especialmente se houver muitos ambientes.
    """
    return sorted(entries, key=lambda x: (x[0] != "base", x[0].lower()))


def print_table(entries: Iterable[Tuple[str, str]]) -> None:
    """
    Imprime os dados em formato de tabela alinhada com duas colunas:
        - 'Env' (nome do ambiente)
        - 'Python' (caminho do executável)

    Lógica de formatação:
        - A largura da coluna 'Env' é calculada com base no maior nome presente,
          garantindo alinhamento limpo.
    """
    # Converte para lista (pode ter sido um iterador) e calcula a largura da coluna 1
    entries = list(entries)
    name_width = max(len("Env"), *(len(name) for name, _ in entries)) if entries else len("Env")

    # Cabeçalho
    print(f"{'Env':<{name_width}}  Python")
    print(f"{'-' * name_width}  {'-' * 6}")

    # Linhas
    for name, path in entries:
        print(f"{name:<{name_width}}  {path}")


def main() -> None:
    """
    Função principal:
        - Coleta as informações do Conda.
        - Monta a lista (nome, caminho_python).
        - Ordena a saída.
        - Exibe a tabela no console.
    """
    info = run_conda_info_json()
    entries = collect_env_entries(info)
    entries = sort_entries(entries)
    print_table(entries)


if __name__ == "__main__":
    # Protege contra execução acidental ao importar este arquivo como módulo
    main()
