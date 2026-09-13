# Plano de Implementação — Menus Interativos com Questionary

> **Ciclo:** `001`
> **Status:** `Concluído`
> **Versão:** `v1`
> **Data de criação:** 2026-09-13
> **Última atualização:** 2026-09-13
> **Tipo:** `feature`
> **Prioridade:** `P1`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO PARA APROVAÇÃO`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-09-13`

## Objetivo

Implementar uma interface interativa moderna no terminal (com navegação por setas e caixas de seleção via `questionary`), proporcionando o "melhor dos dois mundos":
1. **Uso diário guiado:** `belt`, `belt restic` e `belt docker` abrem menus interativos quando chamados sem argumentos em terminais TTY.
2. **Automação via CLI:** comandos diretos como `belt restic backup --dry-run` continuam funcionando plenamente para scripts e agendamentos não-interativos.

## Contexto e baseline

Após a fundação da CLI (Ciclo 000), o uso dos comandos do Docker e Restic requeria a digitação de subcomandos e parâmetros específicos, ou o menu simples numérico. Menus visuais modernos facilitam a operação diária no Windows PowerShell/CMD e Linux sem comprometer a automação.

## Escopo

### Dentro do escopo
- Adição da dependência `questionary>=2.0.0` no `pyproject.toml`.
- Módulo `src/utility_belt/ui/restic_menu.py`: assistente passo a passo, backup (com `--dry-run`), restauração com seleção de snapshots, verificação e configuração.
- Módulo `src/utility_belt/ui/docker_menu.py`: checklist interativa para exportação múltipla de imagens e seleção direta de arquivos `.tar` para importação.
- Atualização do menu principal `src/utility_belt/menu.py` para utilizar `questionary`.
- Atualização das callbacks do Typer (`invoke_without_command=True`) em `cli.py`, `adapters/restic.py` e `adapters/docker.py`.
- Testes unitários completos cobrindo callbacks sem comandos e navegação interativa em `tests/test_interactive_menus.py`.

### Fora do escopo
- TUI complexa em tela cheia com Textual ou Curses.
- Modificação no comportamento dos comandos CLI com argumentos.

## Decisões e autoridades
- **Decisão /grill-me:** Invocação direta de menus ao chamar comandos sem argumentos em terminais interativos.
- **Biblioteca de UI:** `questionary` (baseada em `prompt_toolkit`), garantindo portabilidade entre Windows e Linux.

## Estratégia de testes
- Testes unitários em `tests/test_interactive_menus.py` validando que as callbacks `invoke_without_command` chamam os menus corretos quando nenhum subcomando é passado.
- Garantia de que a suíte completa de testes (`51 items`) continua passando sem regressões.

## Arquivos afetados
- `pyproject.toml`
- `src/utility_belt/ui/__init__.py`
- `src/utility_belt/ui/restic_menu.py`
- `src/utility_belt/ui/docker_menu.py`
- `src/utility_belt/menu.py`
- `src/utility_belt/cli.py`
- `src/utility_belt/adapters/restic.py`
- `src/utility_belt/adapters/docker.py`
- `tests/test_interactive_menus.py`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| PR | [#3](https://github.com/EuThiagoAndrade/utility-belt/pull/3) |
| Commits de entrega | `951a342`, `f613ae8` |
| Handoff Schema Version | `1` |
| Local do plano | `_project/executed/001_menus_interativos/001_plan.md` |

## Revisão crítica

- **Data:** 2026-09-13
- **Veredito:** `APTO PARA APROVAÇÃO`
- **Aprovação humana pós-revisão:** Aprovada em 2026-09-13
- **Observações:** Aprovado via entrevista /grill-me e integrado com sucesso.
