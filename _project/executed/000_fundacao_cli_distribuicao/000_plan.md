# Plano de Implementação — Fundação CLI e Distribuição

> **Ciclo:** `000`
> **Status:** `Concluído`
> **Versão:** `v1`
> **Data de criação:** 2026-09-11
> **Última atualização:** 2026-09-13
> **Tipo:** `feature`
> **Prioridade:** `P0`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO PARA APROVAÇÃO`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-09-11`

## Objetivo

Implementar a arquitetura base do canivete suíço de terminal `utility-belt` (`belt`), permitindo adicionar ferramentas ao repositório, distribuí-las em pacote único instalável por usuário e atualizar máquinas Windows e Linux com um único comando (`uv tool upgrade utility-belt`).

## Contexto e baseline

O projeto iniciou com scripts dispersos em pastas (`docker/` e `restic/`) que utilizavam `input()` síncrono, caminhos hardcoded para Windows (`C:\Programas`, `D:\Restic-Programas`) e dependiam de execução manual no checkout. Não havia CLI unificada, empacotamento, testes ou distribuição entre máquinas.

## Escopo

### Dentro do escopo
- Estrutura base de pacote Python com `pyproject.toml`, layout `src/` e entry point `belt` / `utility-belt`.
- CLI central com Typer fornecendo `belt --help`, `belt --version`, `belt list`, `belt doctor`, `belt menu` e `belt run`.
- Catálogo de ferramentas declarativo baseado em manifestos `tool.toml` carregados via `importlib.resources`.
- Executor de subprocessos (`runner.py`) isolado, preservando o `cwd` do usuário e com `-ExecutionPolicy Bypass` em processos PowerShell no Windows.
- Ferramenta piloto `system.info` para validação segura de ponta a ponta.
- Adaptadores e wrappers para as ferramentas existentes: `docker` (export/import) e `restic` (backup/restore/check).
- Configuração local via `platformdirs` e persistência atômica em TOML via `tomli-w`.
- Suíte inicial de testes unitários com `pytest` e linting com `ruff`.

### Fora do escopo
- Marketplace de ferramentas, download dinâmico em runtime ou serviço daemon residente.
- Gerenciamento de segredos em nuvem (senhas do restic mantidas em memória).
- Pastas legadas não utilizadas (`Conda/`, `Utilitarios/`).

## Decisões e autoridades
- **ADR-001:** Governança agnóstica com adapters de descoberta.
- **ADR-002:** Arquitetura CLI distribuível via `uv`, `typer`, `platformdirs` e `tomli-w`.

## Estratégia de testes
- Testes unitários do catálogo, CLI, runner, diagnósticos e adaptadores em `tests/`.
- Mocking de chamadas de subprocessos e inspeção de saída de terminal.
- Validação com `pytest` e checagem de estilo com `ruff`.

## Itens de implementação

### 1. Fundação e empacotamento
- `pyproject.toml` com build backend Hatchling e inclusão expressa de pacotes e ferramentas.
- Entry points `belt` e `utility-belt` apontando para `utility_belt.cli:main`.

### 2. Catálogo e execução
- `catalog.py` descobrindo ferramentas via `importlib.resources.files("utility_belt.tools")`.
- `runner.py` executando subprocessos mantendo `cwd = Path.cwd()` e argumentos em lista sem shell injection.

### 3. Configuração e diagnóstico
- `config.py` gerenciando perfis e escrita atômica com `tomli-w`.
- `doctor.py` avaliando integridade do ambiente e pré-requisitos de ferramentas.

### 4. Adaptadores Docker e Restic
- `utility_belt/adapters/docker.py` e `utility_belt/adapters/restic.py` mapeando subcomandos CLI aos scripts de automação.
- Migração transparente de configurações legadas do `ResticMenu`.

## Arquivos afetados
- `pyproject.toml`
- `src/utility_belt/*`
- `tests/*`
- `README.md`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Commit de entrega | `8d8a028` |
| Handoff Schema Version | `1` |
| Local do plano | `_project/executed/000_fundacao_cli_distribuicao/000_plan.md` |

## Revisão crítica

- **Data:** 2026-09-11
- **Veredito:** `APTO PARA APROVAÇÃO`
- **Aprovação humana pós-revisão:** Aprovada em 2026-09-11
- **Observações:** Priorizar CLI e distribuição antes de menus complexos; inclusão de dados do pacote explicitada no build.
