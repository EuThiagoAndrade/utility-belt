---
title: "Arquitetura CLI distribuível e isolamento de ferramentas"
tags:
  - arquitetura
  - cli
  - distribuicao
author: "Thiago Andrade"
module: "Núcleo CLI"
last_updated: "2026-09-13"
origin_cycle: "000"
---

# ADR-002: Arquitetura CLI distribuível e isolamento de ferramentas

## Status

Aceito

## Contexto

O `utility-belt` tem como meta central servir como um canivete suíço de terminal para ambientes Windows e Linux. Usuários precisam adicionar ferramentas ao repositório, publicá-las em releases e atualizar múltiplas máquinas com um único comando (`uv tool upgrade utility-belt`), sem necessidade de clonar repositórios, ativar ambientes virtuais manualmente ou copiar scripts avulsos. Além disso, as ferramentas suportam automações em Python, scripts PowerShell e ferramentas externas como Docker e Restic.

## Decisão

Adotar uma arquitetura modular baseada nas seguintes diretrizes:

1. **Empacotamento e Distribuição:**
   - Pacote Python padronizado com `pyproject.toml`, layout `src/` e build backend `hatchling`.
   - Entry points `belt` e `utility-belt` instaláveis de forma isolada via `uv tool install` e atualizáveis via `uv tool upgrade`.
   - Inclusão explícita de metadados e arquivos não-Python (`tool.toml`, scripts auxiliares) no wheel através de configurações de build do Hatchling.

2. **Núcleo de Interface de Linha de Comando (CLI):**
   - Construído com `typer` para subcomandos, ajuda (`--help`), autocompletion e validação tipada.
   - Menus interativos com `questionary` invocados automaticamente quando comandos forem chamados sem argumentos em terminais interativos (TTY), preservando execução não-interativa estrita para scripts e automações.

3. **Catálogo de Ferramentas e Descoberta:**
   - Ferramentas declaradas via `tool.toml` organizadas sob `src/utility_belt/tools/`.
   - Descoberta feita exclusivamente por inspeção do pacote instalado via `importlib.resources.files("utility_belt.tools")`, nunca vasculhando pastas arbitrárias no disco.

4. **Diretório de Trabalho (`cwd`) e Execução Segura:**
   - O diretório de trabalho do processo filho é sempre o diretório corrente do usuário (`Path.cwd()`), garantindo que caminhos relativos passados como argumentos resolvam na pasta do usuário e não dentro de `site-packages`.
   - Argumentos passados em lista com `shell=False` para prevenir injeção de comandos.
   - Em scripts PowerShell no Windows, subprocessos são invocados com `-ExecutionPolicy Bypass` no nível de processo, sem alterar a política de segurança global do sistema operacional.

5. **Armazenamento Local e Configurações:**
   - Diretórios de configuração, cache e logs resolvidos via `platformdirs`, respeitando as convenções do Windows e padrões XDG no Linux.
   - Escrita atômica e serialização de arquivos TOML via biblioteca pura `tomli-w`.

## Consequências

### Positivas
- Instalação e atualização de máquinas com zero atrito via `uv tool`.
- Paridade de experiência entre Windows e Linux.
- Adição de novas ferramentas sem necessidade de modificar a lógica central da CLI.
- Resolução correta e previsível de caminhos de arquivos relativos do usuário.

### Trade-offs
- Execução por subprocessos adiciona pequena sobrecarga em comparação a chamadas de funções Python em memória.
- Dependência do runtime de execução do Python 3.11+ e `uv` na máquina cliente.
