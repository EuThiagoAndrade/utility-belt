"""Menu interativo de terminal para o Utility Belt."""

from __future__ import annotations

import sys

from utility_belt.catalog import catalog
from utility_belt.doctor import run_diagnostics
from utility_belt.runner import run_tool


def show_menu() -> None:
    """Exibe o menu principal interativo do Utility Belt."""
    if not sys.stdin.isatty():
        print("Erro: O comando 'belt menu' requer um terminal interativo (TTY).", file=sys.stderr)
        sys.exit(2)

    while True:
        print("\n===================================================")
        print("           UTILITY BELT - CANIVETE SUÍÇO")
        print("===================================================")
        print(" 1. Listar ferramentas disponíveis")
        print(" 2. Diagnóstico do ambiente (Doctor)")
        print(" 3. Executar ferramenta")
        print(" 0. Sair")
        print("---------------------------------------------------")

        try:
            escolha = input("Selecione uma opção: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando menu.")
            break

        if escolha in {"0", "sair", "exit", "q"}:
            print("Até logo!")
            break

        if escolha == "1":
            tools = catalog.list_tools()
            print("\nFerramentas instaladas:")
            for i, tool in enumerate(tools, 1):
                compat = "[OK]" if tool.is_compatible else "[Incompatível]"
                print(f"  {i}. {tool.id:<20} {compat} - {tool.name}")
            input("\nPressione Enter para continuar...")

        elif escolha == "2":
            diag = run_diagnostics()
            print("\nDiagnóstico Rápido:")
            print(f"  SO: {diag['system']['os_name']} ({diag['system']['architecture']})")
            print(f"  Python: {diag['python']['version']}")
            print(f"  Docker: {'Instalado' if diag['dependencies']['docker']['installed'] else 'Não encontrado'}")
            print(f"  Restic: {'Instalado' if diag['dependencies']['restic']['installed'] else 'Não encontrado'}")
            input("\nPressione Enter para continuar...")

        elif escolha == "3":
            tools = catalog.list_tools()
            print("\nEscolha a ferramenta para executar:")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.id} ({tool.name})")
            print("  0. Voltar")

            try:
                sub = input("\nNúmero da ferramenta: ").strip()
                if sub in {"0", "sair"}:
                    continue
                if sub.isdigit() and 1 <= int(sub) <= len(tools):
                    selected = tools[int(sub) - 1]
                    print(f"\n--- Executando: {selected.id} ---")
                    code = run_tool(selected, args=[])
                    print(f"\n--- Concluído com código: {code} ---")
                else:
                    print("Opção inválida.")
            except (KeyboardInterrupt, EOFError):
                continue
            input("\nPressione Enter para continuar...")
        else:
            print("Opção inválida. Tente novamente.")
